
subroutine pyinitswitch(switch_legacy, parmpath)
    use msis_init, only: msisinit

    implicit none

    real(4), intent(in), optional             :: switch_legacy(1:25)      !Legacy switch array
    character(len=*), intent(in), optional    :: parmpath                 !Path to parameter file

    call msisinit(switch_legacy=switch_legacy, parmpath=parmpath)

    return
end subroutine pyinitswitch

subroutine pymsiscalc(day, utsec, lon, lat, z, sfluxavg, sflux, ap, output, n)
    ! NOTE: pymsiscalc takes the order (lon, lat, z), but the msiscalc Fortran
    !       code takes the order (z, lat, lon)
    use msis_calc, only: msiscalc
    use msis_constants, only: rp

    implicit none

    integer, intent(in)        :: n
    real(kind=rp), intent(in)  :: day(n)
    real(kind=rp), intent(in)  :: utsec(n)
    real(kind=rp), intent(in)  :: lon(n)
    real(kind=rp), intent(in)  :: lat(n)
    real(kind=rp), intent(in)  :: z(n)
    real(kind=rp), intent(in)  :: sfluxavg(n)
    real(kind=rp), intent(in)  :: sflux(n)
    real(kind=rp), intent(in)  :: ap(n, 1:7)
    real(kind=rp), intent(out) :: output(n, 1:11)

    integer :: i

    do i=1, n
        call msiscalc(day(i), utsec(i), z(i), lat(i), lon(i), sfluxavg(i), &
                    sflux(i), ap(i, :), output(i, 11), output(i, 1:10))
    enddo

    return
end subroutine pymsiscalc
