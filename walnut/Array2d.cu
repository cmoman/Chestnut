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

#include "Array2d.h"

namespace Walnut {

template <typename T>
Array2d<T>::Array2d(T *data, int width, int height) {
  this->data = data;
  this->width = width;
  this->height = height;
}

template <typename T>
Array2d<T>::Array2d(thrust::device_vector<T> &vector, int width, int height) {
  data = thrust::raw_pointer_cast(&(vector[0]));
  this->width = width;
  this->height = height;
}

WALNUT_INIT_STRUCT(Array2d);

} // namespace Walnut
