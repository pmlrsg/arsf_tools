#ifndef VEC3D_H
#define VEC3D_H

#include<cstdlib>
#include<vector>

class Vec3d
{
public:
   Vec3d(){data=new double[3];Set(0,0,0);}
   Vec3d(double a,double b,double c){data=new double[3];Set(a,b,c);}
   Vec3d(const Vec3d& copy){data=new double[3];data[0]=copy[0];data[1]=copy[1];data[2]=copy[2];}

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
   Vec3d& operator*(const Vec3d &v);
   Vec3d& operator*(const double d);

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

#endif
