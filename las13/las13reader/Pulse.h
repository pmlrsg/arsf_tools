#ifndef PULSE_H
#define PULSE_H
#include "vec3d.h"
#include "Types.h"

#include <vector>
#include <iostream>
#include <fstream>

/// @authors Milto Miltiadou, supported by the Centre for DIgital Entertainment at the University of Bath, and Plymouth Marine Laboratory
//The code is released under the GNU General Public License v3.0.
//It reads a LAS1.3 file under the LAS specification version 1.3-R11 released October 24, 2010 (Available at: http://www.asprs.org/a/society/committees/standards/LAS_1_3_r11.pdf), using only the Point Data Record Format 4.
//The original script was written in Python and it's available here: https://github.com/pmlrsg/arsf_tools and a lot of the comments were copied that Python script and the LAS1.3 file specifications

class Pulse
{
    friend class PulseManager;

public:
   //--------------------------------------------------------------------------
   /// @brief default constructor
   //--------------------------------------------------------------------------
   Pulse(const Types::Public_Header_Block &i_publicHeader,
       const Types::WF_packet_Descriptor &i_wv_info,
       const Types::Data_Point_Record_Format_4 &i_point_info,
       const char *wave_data,
       int wave_offset);
   //--------------------------------------------------------------------------
   /// @brief copy constructor
   //--------------------------------------------------------------------------
   Pulse(const Pulse &i_pulse);
   //--------------------------------------------------------------------------
   /// @brief method that returns true if the pulse is inside the user limits
   /// @param[in] i_limits the limits of area of our interest
   /// @returns boolean whether the pulse is insise the given limits or not
   //--------------------------------------------------------------------------
   bool isInsideLimits(const std::vector<double> &i_user_limits)const;
   //--------------------------------------------------------------------------
   /// @brief method that adds a discrete point
   //--------------------------------------------------------------------------
   void addDiscretePoint(
           const Types::Public_Header_Block &i_publicHeader,
           const Types::Data_Point_Record_Format_4 &i_point_info
           );
   //--------------------------------------------------------------------------
   /// @brief method that adds a discrete point
   /// @param[in] i_point the position of the point
   /// @param[in] i_intensity the intensity of the point
   //--------------------------------------------------------------------------
   void addDiscretePoint(Vec3d i_point,
           unsigned short i_intensity,
            double i_pointInWaveform
           );
   //--------------------------------------------------------------------------
   /// @brief method that prints all the attributes associated with this pulse
   //--------------------------------------------------------------------------
   void print()const;
   //--------------------------------------------------------------------------
   /// @brief method that returns the origin of the point
   //--------------------------------------------------------------------------
   const Vec3d &getOrigin(){return m_origin;}
   //--------------------------------------------------------------------------
   /// @brief method that returns the offset of the point
   //--------------------------------------------------------------------------
   const Vec3d &getOffset(){return m_offset;}
   //--------------------------------------------------------------------------
   /// @brief method that returns the wave offset of the waveform packet
   /// used to identify waveforms and match 2nd,3rd and 4rd returns of the beam
   //--------------------------------------------------------------------------
   int getWaveOffset(){return m_waveOffset;}
   //-------------------------------------------------------------------------
   /// @brief the kernel used to smooth the wave
   /// @note normalised factor does not have to be included
   //-------------------------------------------------------------------------
   static std::vector<float> s_kernel;
   //--------------------------------------------------------------------------
   /// @brief default destructor
   //--------------------------------------------------------------------------
   ~Pulse();


   //--------------------------------------------------------------------------
   //Fudge factors for python code: swig - there is a better way but I can't get it to work
   //--------------------------------------------------------------------------

   //Functions for returning waveform
   bool sampleinwf(unsigned int s){if(s<m_noOfSamples){return true;}else{return false;}}
   int sampleintensity(unsigned int sample){if(sampleinwf(sample)){return m_returns[sample];}else{return 0;}}
   std::vector<double> sampleXYZ(unsigned int sample){if(sampleinwf(sample)){return (m_origin+(m_offset*sample)).AsStdVector();}else{return std::vector<double>(3,0);}}

   //Functions for returning other data
   double time(){return m_time;}
   int nreturns(){return (int)m_numberOfReturnsForThisPulse;}
   int nsamples(){return m_noOfSamples;}
   int classification(){return (int)m_classification;}
   int scanangle(){return (int)m_scanAngle;}
   std::vector<double> pointinwaveform(){return m_discretePointInWaveform;}
   std::vector<double> returnpointlocation(){return m_discreteReturnPointLocation;}
   std::vector<int> discreteintensities(){return m_discreteIntensities;}
   std::vector<double> originXYZ(){return m_origin.AsStdVector();}
   std::vector<double> offsetXYZ(){return m_offset.AsStdVector();}
   const double sampletime()const{return m_temporalSampleSpacing;}

private:

   //--------------------------------------------------------------------------
   /// @brief
   //--------------------------------------------------------------------------
   char *m_returns;

   Vec3d m_point;

   char m_returnNumber;

   char m_numberOfReturnsForThisPulse;

   double m_time;

   char m_scanAngle;
   // ---------------------------------------------------------------
   //  0 created, never classified
   //  1 Unclassified
   //  2 Ground
   //  3 Low Vegetation
   //  4 Medium Vegetation
   //  5 High Vegetation
   //  6 Building
   //  7 Low Point (noise)
   //  8 model Key-point (mass point)
   //  9 water
   // 10- 11 reserved for ASPRS definition
   // 12 overlap points
   // 13-31 reserved for ASPRS definition
   // ---------------------------------------------------------------
   char m_classification;

   double m_temporalSampleSpacing;

   unsigned char m_AGCgain;

   double m_digitiserGain;

   double m_digitiserOffset;

   unsigned int m_noOfSamples;

   double m_sampleLength;

   double m_returnPointLocation;

   double m_pointInWaveform;

   Vec3d m_offset;

   Vec3d m_origin;
   //-------------------------------------------------------------------------
   /// @brief meters per nanosecond
   //-------------------------------------------------------------------------
   #ifdef SWIG
   static const double c_light_speed = 0.299792458;
   #else
   static constexpr double c_light_speed = 0.299792458;
   #endif
   //-------------------------------------------------------------------------
   /// @brief all the discrete points of the pulse
   //-------------------------------------------------------------------------
   std::vector<Vec3d> m_discretePoints;
   //-------------------------------------------------------------------------
   /// @brief the corresponding intensities of the discrete points
   //-------------------------------------------------------------------------
   std::vector<int> m_discreteIntensities;
   //-------------------------------------------------------------------------
   /// @brief waveform packet offset in the binary file
   /// used to identify discrete points associated with the same waveform
   //-------------------------------------------------------------------------
   int m_waveOffset;


   std::vector<double> m_discretePointInWaveform;
   std::vector<double> m_discreteReturnPointLocation;


};

#endif // PULSE_H
