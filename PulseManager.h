#ifndef PULSEMANAGER_H
#define PULSEMANAGER_H

#include "Pulse.h"
#include "Types.h"
#include "vec3d.h"

#include <unordered_map>
#include <vector>
#include <iomanip>

/// @authors Milto Miltiadou, supported by the Centre for DIgital Entertainment at the University of Bath, and Plymouth Marine Laboratory
//The code is released under the GNU General Public License v3.0.
//It reads a LAS1.3 file under the LAS specification version 1.3-R11 released October 24, 2010 (Available at: http://www.asprs.org/a/society/committees/standards/LAS_1_3_r11.pdf), using only the Point Data Record Format 4.
//The original script was written in Python and it's available here: https://github.com/pmlrsg/arsf_tools and a lot of the comments were copied that Python script and the LAS1.3 file specifications


class PulseManager
{
public:
   //-------------------------------------------------------------------------
   /// @brief default constructor
   /// @param[in] i_wv_info
   //-------------------------------------------------------------------------
   PulseManager(
           const Types::Public_Header_Block &i_publicHeader,
           const Types::WF_packet_Descriptor &i_wv_info
           );
   //-------------------------------------------------------------------------
   /// @brief copy constructor
   /// @param[in] i_pulseManager object to be copied
   //-------------------------------------------------------------------------
   PulseManager(const PulseManager &i_pulseManager);
   //-------------------------------------------------------------------------
   /// @brief method that adds a fw pulse to the manager
   /// @param[in] i_point
   /// @param[in] wave_data  information of the wave
   /// @param[in] wave_offset the offset of the wave in the binary file
   //-------------------------------------------------------------------------
   void addPoint(
           const Types::Data_Point_Record_Format_4 &i_point,
           const char *wave_data,
           int wave_offset
                 );
   //-------------------------------------------------------------------------
   /// @brief method that adds a discrete point that is not associated with
   /// any waveform
   /// @param[in] i_position the position of the discrete point
   /// @param[in] i_intensity the
   //-------------------------------------------------------------------------
   void addUnAssociatedDiscretePoint(
           const Types::Data_Point_Record_Format_4 &i_point_info
           );
   //-------------------------------------------------------------------------
   /// @brief method that sorts the discrete points into the pulses
   //-------------------------------------------------------------------------
   void sortDiscretePoints(
           const std::vector<Vec3d> &m_discretePoints,
           const std::vector<unsigned short> &m_discreteIntensities,
           const std::vector<int> &m_discreteWaveOffsets,
           const std::vector<double> &m_discretePointInWaveform
           );
   //-------------------------------------------------------------------------
   /// @brief method that returns the number of pulses;
   //-------------------------------------------------------------------------
   unsigned int getNumOfPulses(){return m_pulses.size();}
   //-------------------------------------------------------------------------
   /// @brief method that returns the number of discrete points that are not
   /// associated with any waveform
   //-------------------------------------------------------------------------
   unsigned int getNumOfAloneDiscretePoints(){return m_discretePoints.size();}
   //-------------------------------------------------------------------------
   /// @brief method that prints all the information about a given pulse
   /// @param[in] i_pulse the index of the pulse of our interest
   //-------------------------------------------------------------------------
   void printPulseInfo(unsigned int i_pulse);
   //-------------------------------------------------------------------------
   /// @brief method that sets the noise level
   /// @param[in] i_noiseLevel the new noise level
   //-------------------------------------------------------------------------
   void setNoiseLevel(double i_noiseLevel);
   //-------------------------------------------------------------------------
   /// @brief default destructor
   //-------------------------------------------------------------------------
   ~PulseManager();
   //-------------------------------------------------------------------------
   /// @brief return a pointer to the requested pulse object
   //-------------------------------------------------------------------------
   Pulse* getPulse(unsigned int i_pulse){if(i_pulse < getNumOfPulses()) {return m_pulses[i_pulse];}else{return NULL;}}

private:
   //-------------------------------------------------------------------------
   /// @brief method that sorts the pulses with respect to the y position of
   /// their origins
   //-------------------------------------------------------------------------
   void sortPulseWithRespectToY();

   //-------------------------------------------------------------------------
   /// @brief public header block
   //-------------------------------------------------------------------------
   Types::Public_Header_Block m_public_header;
   //-------------------------------------------------------------------------
   /// @brief waveform packet descriptor
   //-------------------------------------------------------------------------
   Types::WF_packet_Descriptor m_wfInfo;
   //-------------------------------------------------------------------------
   /// @brief sort the pulses according to there wave offset for easy search
   /// while trying to associate the discrete points with the pulses
   //-------------------------------------------------------------------------
   std::unordered_map <  int , unsigned int> myMap;

   //-------------------------------------------------------------------------
   std::vector<Pulse *> m_pulses;
   //-------------------------------------------------------------------------
   /// @brief discrete points that are not associated with any waveform
   //-------------------------------------------------------------------------
   std::vector<Vec3d> m_discretePoints;
   //-------------------------------------------------------------------------
   /// @brief the corresponding intensities of discrete points without
   /// waveform
   //-------------------------------------------------------------------------
   std::vector<unsigned short> m_discreteIntensities;
   //-------------------------------------------------------------------------
   /// @brief the noise Level
   //-------------------------------------------------------------------------
   double m_noiseLevel;

};

#endif // PULSEMANAGER_H
