#ifndef PULSEMANAGER_H
#define PULSEMANAGER_H

#include "Pulse.h"
#include "Types.h"

#include <unordered_map>
#include <vector>
#include <gmtl/Vec.h>
#include <iomanip>

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
           const std::vector<gmtl::Vec3f> &m_discretePoints,
           const std::vector<unsigned short> &m_discreteIntensities,
           const std::vector<int> &m_discreteWaveOffsets
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
   std::vector<gmtl::Vec3f> m_discretePoints;
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
