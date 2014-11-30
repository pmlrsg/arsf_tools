#ifndef VEC3D_H
#define VEC3D_H

//The code is released under the GNU General Public License v3.0.

#include<cstdlib>
#include<vector>
#include<iostream>

class Vec3d
{
public:
   Vec3d(){data=new double[3];Set(0,0,0);}
   Vec3d(double a,double b,double c){data=new double[3];Set(a,b,c);}
   Vec3d(const Vec3d& copy){data=new double[3];data[0]=copy.data[0];data[1]=copy.data[1];data[2]=copy.data[2];}

   ~Vec3d()
   {
      if(data!=NULL)
      {
         delete[] data;
         data=NULL;
      }
   }

   Vec3d operator+(const Vec3d &v);
   Vec3d operator-(const Vec3d &v);
   Vec3d& operator=(const Vec3d &v);
   Vec3d operator*(const Vec3d &v);
   template<class T>
   Vec3d operator*(const T d)
   {
      Vec3d result;
      for(int i=0;i<3;i++)
      {
         result.data[i]=data[i]*d;
      } 
      return result;
   }

   double operator [](int i)const{return data[i];}
   double &operator [](int i){return data[i];}

   void Set(double a,double b,double c){data[0]=a;data[1]=b;data[2]=c;}

   std::vector<double> AsStdVector() const
   {
      return std::vector<double> (data,data+3);
   }
   
   const double* AsDoubleArray()const
   {
      return data;
   }

private:
   double* data;
};

//Wrapper to allow multiplication by scalar on the left hand side
template <class T>
Vec3d operator*(T const scalar, Vec3d& rhs)
{ 
   return (rhs*scalar);
}

#endif
