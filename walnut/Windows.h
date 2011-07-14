/*
 *   Copyright 2011 Andrew Stromme <astromme@chatonka.com>
 *
 *   This program is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as
 *   published by the Free Software Foundation; either version 2, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details
 *
 *   You should have received a copy of the GNU Library General Public
 *   License along with this program; if not, write to the
 *   Free Software Foundation, Inc.,
 *   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */

#ifndef WINDOWS_H
#define WINDOWS_H

#include "walnut_global.h"
#include "Array2d.h"

namespace Walnut {

template <typename T>
struct WALNUT_EXPORT Window2d {

  Array2d<T> array;

  int m_xLocation;
  int m_yLocation;

  __host__ __device__ Window2d(Array2d<T> &data, int x, int y) : array(data), m_xLocation(x), m_yLocation(y) {}
  __host__ __device__ Window2d(const Window2d<T> &other) : array(other.array), m_xLocation(other.m_xLocation), m_yLocation(other.m_yLocation) {}

  __host__ __device__
  T& shiftedData(int x_offset, int y_offset) {
    return array.data[array.calculateIndex(m_xLocation, m_yLocation, x_offset, y_offset)];
  }

  __host__ __device__ T& topLeft()     { return shiftedData(-1, -1); }
  __host__ __device__ T& top()         { return shiftedData( 0, -1); }
  __host__ __device__ T& topRight()    { return shiftedData( 1, -1); }
  __host__ __device__ T& left()        { return shiftedData(-1,  0); }
  __host__ __device__ T& center()      { return shiftedData( 0,  0); }
  __host__ __device__ T& right()       { return shiftedData( 1,  0); }
  __host__ __device__ T& bottomLeft()  { return shiftedData(-1,  1); }
  __host__ __device__ T& bottom()      { return shiftedData( 0,  1); }
  __host__ __device__ T& bottomRight() { return shiftedData( 1,  1); }

};

}

#endif // WINDOWS_H
