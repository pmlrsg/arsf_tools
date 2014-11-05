#include "vec3d.h"

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

Vec3d& Vec3d::operator*(const Vec3d &v)
{
   for(int i=0;i<3;i++)
   {
      data[i]=data[i]*v.data[i];
   }
   return *this;
}

Vec3d& Vec3d::operator*(const double d)
{
   for(int i=0;i<3;i++)
   {
      data[i]=data[i]*d;
   } 
   return *this;
  
}
