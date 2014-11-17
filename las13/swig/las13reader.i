 /* las13reader.i */
 %module las13reader
 %{
 /* header files and function declarations here */
 #define SWIG_FILE_WITH_INIT
#include "../las13reader/src/Las1_3_handler.h" 
#include "../las13reader/src/PulseManager.h" 
#include "../las13reader/src/Pulse.h" 
 %}

%include "typemaps.i"
%include "std_string.i"
%include "std_map.i"
%include "../las13reader/src/Las1_3_handler.h" 
/*Rename must be before the class that is being wrapped - this line renames [] to __getitem__ for python*/
%rename(__getitem__) PulseManager::operator[];
%include "../las13reader/src/PulseManager.h" 
%include "../las13reader/src/Pulse.h" 

%apply const std::string& {std::string* foo};

%include "carrays.i"
%array_function(float, floatArray);
%array_function(double, doubleArray);

%include "std_vector.i";
namespace std {
    %template(vector_int) vector<int>;
    %template(vector_double) vector<double>;
    %template(vector_float) vector<float>;
    %template(vector_vector) vector< vector<double> >;
} 


%typemap(out) double * {
  int i;
  $result = PyList_New(3);
  for (i = 0; i < 3; i++) {
    PyObject *o = PyFloat_FromDouble((double) $1[i]);
    PyList_SetItem($result,i,o);
  }
}

