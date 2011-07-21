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

#ifndef POINTS_H
#define POINTS_H

#include "walnut_global.h"

namespace Walnut {

struct Point1d
{
  int32 x;
  __device__ Point1d(int32 x_) : x(x_) {}
};

struct Point2d {
  int32 m_x;
  int32 m_y;
  __host__ __device__ Point2d(int32 x_=0, int32 y_=0) : m_x(x_), m_y(y_) {}
  __host__ __device__ int32& x() { return m_x; }
  __host__ __device__ int32& y() { return m_y; }

  __host__ __device__ int32 x() const { return m_x; }
  __host__ __device__ int32 y() const { return m_y; }
};

struct Point3d {
  int32 x;
  int32 y;
  int32 z;
  __device__ Point3d(int32 x_, int32 y_, int32 z_) : x(x_), y(y_), z(z_) {}
};

struct Point4d {
  int32 x;
  int32 y;
  int32 z;
  int32 w;
  __device__ Point4d(int32 x_, int32 y_, int32 z_, int32 w_) : x(x_), y(y_), z(z_), w(w_) {}
};

}

#endif // POINTS_H
