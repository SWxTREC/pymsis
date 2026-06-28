
subroutine pyinitswitch(switch_legacy, parmpath)
    use msis_calc, only: msiscalc
    use msis_constants, only: rp
    use msis_init, only: msisinit

    implicit none

    real(4), intent(in), optional             :: switch_legacy(1:25)      !Legacy switch array
    character(len=*), intent(in), optional    :: parmpath                 !Path to parameter file
    real(kind=rp)                             :: output = 0.
    real(kind=rp)                             :: output_arr(1:11) = 0.

    call msisinit(switch_legacy=switch_legacy, parmpath=parmpath)

    ! Artificially call msiscalc to reset the last variables as there is
    ! a global cache on these and the parameters won't be updated if we
    ! don't set them to something different.
    ! See issue: gh-59
    call msiscalc(0., 0., -999., -999., -1., 0., 0., (/1., 1., 1., 1., 1., 1., 1./), output, output_arr)

    return
end subroutine pyinitswitch

subroutine pymsiscalc(day, utsec, lon, lat, z, sflux, sfluxavg, ap, output, n)
    ! NOTE: pymsiscalc takes the order (lon, lat, z), but the msiscalc Fortran
    !       code takes the order (z, lat, lon).
    !       sflux also comes before sfluxavg
    use msis_calc, only: msiscalc
    use msis_constants, only: rp, dmissing
    use, intrinsic :: ieee_arithmetic, only: ieee_value, ieee_quiet_nan

    implicit none

    integer, intent(in)        :: n
    real(kind=rp), intent(in)  :: day(n)
    real(kind=rp), intent(in)  :: utsec(n)
    real(kind=rp), intent(in)  :: lon(n)
    real(kind=rp), intent(in)  :: lat(n)
    real(kind=rp), intent(in)  :: z(n)
    real(kind=rp), intent(in)  :: sflux(n)
    real(kind=rp), intent(in)  :: sfluxavg(n)
    real(kind=rp), intent(in)  :: ap(n, 1:7)
    real(kind=rp), intent(out) :: output(n, 1:11)

    integer :: i

    ! Zero the output before calling into the model. There are some issues with
    ! potential nan-leakage on unitiailzed arrays in free-threading builds,
    ! so just set it to 0 to avoid any potential issues.
    output = 0.0_rp

    do i=1, n
        call msiscalc(day(i), utsec(i), z(i), lat(i), lon(i), sfluxavg(i), &
                    sflux(i), ap(i, :), output(i, 11), output(i, 1:10))
    enddo

    ! The model marks missing densities with the tiny sentinel ``dmissing``.
    ! Convert those to NaN here so callers receive an unambiguous missing value
    ! and no downstream sentinel matching is required.
    where (output == dmissing) output = ieee_value(1.0_rp, ieee_quiet_nan)

end subroutine pymsiscalc
