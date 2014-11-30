#include "vec3d.h"

//The code is released under the GNU General Public License v3.0.

Vec3d Vec3d::operator+(const Vec3d &v)
{
   Vec3d result;
   for(int i=0;i<3;i++)
   {
      result.data[i]=this->data[i]+v.data[i];
   }
   return result;
}

Vec3d Vec3d::operator-(const Vec3d &v)
{
   Vec3d result;
   for(int i=0;i<3;i++)
   {
      result.data[i]=this->data[i]-v.data[i];
   }
   return result;
}

Vec3d& Vec3d::operator=(const Vec3d &v)
{
   for(int i=0;i<3;i++)
      data[i]=v.data[i];
   return *this;
}

Vec3d Vec3d::operator*(const Vec3d &v)
{
   Vec3d result;
   for(int i=0;i<3;i++)
   {
      result.data[i]=data[i]*v.data[i];
   }
   return result;
}
