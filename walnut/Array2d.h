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

#ifndef ARRAY2D_H
#define ARRAY2D_H

#include "walnut_global.h"
#include <thrust/device_vector.h>

namespace Walnut {

template <typename T>
struct WALNUT_EXPORT Array2d
{
  T *data;
  int width;
  int height;

  Array2d(T *data, int width, int height);
  Array2d(thrust::device_vector<T> &vector, int width, int height);

  const T* constData() const { return (const T*)data; }
  thrust::device_ptr<T> thrustPointer() { return thrust::device_ptr<T>(data); }

  __host__ __device__
  int calculateIndex(int x, int y, int x_offset, int y_offset) const {
    x = ((x + x_offset) + width)  % width;
    y = ((y + y_offset) + height) % height;

    return y*width + x;
  }

  __host__ __device__
  T shiftedData(int x, int y, int x_offset, int y_offset) const {
    return data[calculateIndex(x, y, x_offset, y_offset)];
  }
};

} // namespace Walnut

#endif // ARRAY2D_H
