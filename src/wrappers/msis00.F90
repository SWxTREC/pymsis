subroutine pyinitswitch(switch_legacy, parmpath)
    implicit none

    real(4), intent(in), optional             :: switch_legacy(1:25)      !Legacy switch array
    ! Here for compatibility with MSIS2 even though it is unused
    character(len=*), intent(in), optional    :: parmpath                 !Path to parameter file

    call tselec(switch_legacy)
    call meters(.TRUE.)

    return
end subroutine pyinitswitch

subroutine pymsiscalc(day, utsec, lon, lat, z, sflux, sfluxavg, ap, output, n)
    implicit none

    integer, intent(in)        :: n
    real, intent(in)  :: day(n)
    real, intent(in)  :: utsec(n)
    real, intent(in)  :: lon(n)
    real, intent(in)  :: lat(n)
    real, intent(in)  :: z(n)
    real, intent(in)  :: sflux(n)
    real, intent(in)  :: sfluxavg(n)
    real, intent(in)  :: ap(n, 1:7)
    real, intent(out) :: output(n, 1:11)

    integer :: i
    real :: t(2), d(9), lon_tmp ! Temporary to swap dimensions

    do i=1, n
        if (lon(i) < 0) then
            lon_tmp = lon(i) + 360
        else
            lon_tmp = lon(i)
        endif
        call gtd7d(10000 + FLOOR(day(i)), utsec(i), z(i), lat(i), lon_tmp, &
                   utsec(i)/3600. + lon_tmp/15., sfluxavg(i), &
                   sflux(i), ap(i, :), 48, d, t)
        ! O, H, and N are set to zero below 72.5 km
        ! Change them to NaN instead
        if(z(i) < 72.5) then
            d(2) = 9.99e-38 ! NaN
            d(7) = 9.99e-38 ! NaN
            d(8) = 9.99e-38 ! NaN
        endif
        ! These mappings are to go from MSIS00 locations to MSIS2 locations
        output(i, 1) = d(6)
        output(i, 2) = d(3)
        output(i, 3) = d(4)
        output(i, 4) = d(2)
        output(i, 5) = d(1)
        output(i, 6) = d(7)
        output(i, 7) = d(5)
        output(i, 8) = d(8)
        output(i, 9) = d(9)
        output(i, 10) = 9.99e-38 ! NaN
        output(i, 11) = t(2)
    enddo

    return
end subroutine pymsiscalc


! Deprecated forms of the above functions
subroutine pytselec(switch_legacy)
  implicit none

  real(4), intent(in), optional             :: switch_legacy(1:25)      !Legacy switch array

  WRITE(6, *) 'Warning: pytselec is deprecated and will be removed in a future version. Use pyinitswitch instead.'
  call tselec(switch_legacy)
  call meters(.TRUE.)

  return
end subroutine pytselec

subroutine pygtd7d(day, utsec, lon, lat, z, sflux, sfluxavg, ap, output, n)

implicit none

integer, intent(in)        :: n
real, intent(in)  :: day(n)
real, intent(in)  :: utsec(n)
real, intent(in)  :: lon(n)
real, intent(in)  :: lat(n)
real, intent(in)  :: z(n)
real, intent(in)  :: sflux(n)
real, intent(in)  :: sfluxavg(n)
real, intent(in)  :: ap(n, 1:7)
real, intent(out) :: output(n, 1:11)

integer :: i
real :: t(2), d(9), lon_tmp ! Temporary to swap dimensions

WRITE(6, *) 'Warning: pygtd7d is deprecated and will be removed in a future version. Use pymsiscalc instead.'
do i=1, n
  if (lon(i) < 0) then
    lon_tmp = lon(i) + 360
  else
    lon_tmp = lon(i)
  endif
  call gtd7d(10000 + FLOOR(day(i)), utsec(i), z(i), lat(i), lon_tmp, &
              utsec(i)/3600. + lon_tmp/15., sfluxavg(i), &
              sflux(i), ap(i, :), 48, d, t)
  ! O, H, and N are set to zero below 72.5 km
  ! Change them to NaN instead
  if(z(i) < 72.5) then
    d(2) = 9.99e-38 ! NaN
    d(7) = 9.99e-38 ! NaN
    d(8) = 9.99e-38 ! NaN
  endif
  ! These mappings are to go from MSIS00 locations to MSIS2 locations
  output(i, 1) = d(6)
  output(i, 2) = d(3)
  output(i, 3) = d(4)
  output(i, 4) = d(2)
  output(i, 5) = d(1)
  output(i, 6) = d(7)
  output(i, 7) = d(5)
  output(i, 8) = d(8)
  output(i, 9) = d(9)
  output(i, 10) = 9.99e-38 ! NaN
  output(i, 11) = t(2)
enddo

return
end subroutine pygtd7d
