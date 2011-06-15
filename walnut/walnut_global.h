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

#ifndef WALNUT_GLOBAL
#define WALNUT_GLOBAL

#include <QtCore/QtGlobal>

// Cuda
#include <host_defines.h>
#include <vector_types.h>

#if defined(WALNUT_LIBRARY)
#  define WALNUT_EXPORT Q_DECL_EXPORT
#else
#  define WALNUT_EXPORT Q_DECL_IMPORT
#endif

#define WALNUT_INIT_STRUCT_WITH_TYPE(name, datatype) template struct name<datatype>
#define WALNUT_INIT_STRUCT(name) WALNUT_INIT_STRUCT_WITH_TYPE(name, int); \
                                 WALNUT_INIT_STRUCT_WITH_TYPE(name, char); \
                                 WALNUT_INIT_STRUCT_WITH_TYPE(name, float); \
                                 WALNUT_INIT_STRUCT_WITH_TYPE(name, uchar4)

namespace Walnut {

typedef char    int8;
typedef short   int16;
typedef int     int32;
typedef long    int64;

typedef float   real32;
typedef double  real64;

typedef uchar4   color;

struct WALNUT_EXPORT complex {
  real32 real_part;
  real32 imaginary_part;

  __host__ __device__ complex(real32 real_part, real32 imaginary_part);
  __host__ __device__ real32 magnitude() const;
  __host__ __device__ real32 magnitudeSquared() const;

  __host__ __device__ complex operator*(const complex &other) const;
  __host__ __device__ complex operator+(const complex &other) const;
};

template <typename T> __host__ __device__
inline const T &wMin(const T &a, const T &b) { if (a < b) return a; return b; }

template <typename T> __host__ __device__
inline const T &wMax(const T &a, const T &b) { if (a < b) return b; return a; }

template <typename T> __host__ __device__
inline const T &wBound(const T &min, const T &val, const T &max)
{ return wMax(min, wMin(max, val)); }

}

#endif // WALNUT_GLOBAL
