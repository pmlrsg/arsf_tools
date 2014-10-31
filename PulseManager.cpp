#include "PulseManager.h"
#include <string.h>


//-----------------------------------------------------------------------------
PulseManager::PulseManager(
        const Types::Public_Header_Block &i_publicHeader,
        const Types::WF_packet_Descriptor &i_wv_info
        ):
    m_noiseLevel(30.0)
{
   memcpy((void*) &m_public_header,(void*)&i_publicHeader,sizeof(m_public_header));
   memcpy((void*) &m_wfInfo,(void *) &i_wv_info, sizeof(m_wfInfo));

}

//-----------------------------------------------------------------------------
PulseManager::PulseManager(
        const PulseManager &i_pulseManager
        )
{
    memcpy((void*) &m_public_header,(void*)&i_pulseManager.m_public_header,
           sizeof(m_public_header));
    memcpy((void*) &m_wfInfo,(void *) &i_pulseManager.m_wfInfo,
           sizeof(m_wfInfo));
    m_pulses.resize(i_pulseManager.m_pulses.size());
    for(unsigned int i=0; i<m_pulses.size(); ++i)
    {
        m_pulses[i] = new Pulse(*i_pulseManager.m_pulses[i]);
    }
}

//-----------------------------------------------------------------------------
void PulseManager::setNoiseLevel(double i_noiseLevel)
{
   m_noiseLevel = i_noiseLevel;
}

//-----------------------------------------------------------------------------
void PulseManager::printPulseInfo(unsigned int i_pulse)
{
   if(i_pulse<m_pulses.size())
   {
      m_pulses[i_pulse]->print();
   }
   else
   {
      std::cout << "Pulse with index " << i_pulse << " doesn't exist\n";
   }
}

//-----------------------------------------------------------------------------
void PulseManager::addPoint(
        const Types::Data_Point_Record_Format_4 &i_point,
        const char *wave_data,
        int wave_offset
        )
{
   Pulse *pulse = new Pulse(m_public_header,m_wfInfo,i_point,wave_data,wave_offset);
   m_pulses.push_back(pulse);
   Vec3d origin = m_pulses[m_pulses.size()-1]->getOrigin();
   Vec3d offset = m_pulses[m_pulses.size()-1]->getOffset();
   Vec3d endPoint(offset);
   endPoint=endPoint*(m_wfInfo.number_of_samples);
   endPoint=endPoint+origin;
   m_public_header.max_x = std::max((double)origin[0],m_public_header.max_x);
   m_public_header.max_x = std::max((double)endPoint[0],m_public_header.max_x);
   m_public_header.max_y = std::max((double)origin[1],m_public_header.max_y);
   m_public_header.max_y = std::max((double)endPoint[1],m_public_header.max_y);
   m_public_header.max_z = std::max((double)origin[2],m_public_header.max_z);
   m_public_header.max_z = std::max((double)endPoint[2],m_public_header.max_z);
   std::pair<int,unsigned int> pair(wave_offset,m_pulses.size()-1);
   myMap.insert(pair);
}



//-----------------------------------------------------------------------------
void PulseManager::sortDiscretePoints(
        const std::vector<Vec3d> &m_discretePoints,
        const std::vector<unsigned short> &m_discreteIntensities,
        const std::vector<int> &m_discreteWaveOffsets,
        const std::vector<double> &m_discretePointInWaveform
        )
{
   for(unsigned int i=0; i<m_discreteIntensities.size(); ++i)
   {
      std::unordered_map<int,unsigned int>::const_iterator got =
              myMap.find(m_discreteWaveOffsets[i]);
      if(got == myMap.end())
      {
      }
      else
      {
         m_pulses[got->second]->addDiscretePoint(m_discretePoints[i],
                        m_discreteIntensities[i],m_discretePointInWaveform[i]);
      }
   }
}

//-----------------------------------------------------------------------------
void PulseManager::addUnAssociatedDiscretePoint(
        const Types::Data_Point_Record_Format_4 &i_point_info
        )
{
    Vec3d dpoint(i_point_info.X*m_public_header.x_scale_factor,
                            i_point_info.Y*m_public_header.y_scale_factor,
                            i_point_info.Z*m_public_header.z_scale_factor);
    m_discretePoints.push_back(dpoint);
    m_discreteIntensities.push_back(i_point_info.itensity);
}


//-----------------------------------------------------------------------------
void PulseManager::sortPulseWithRespectToY()
{
    // array to be sorted
    unsigned int len = m_pulses.size();
    // allocate memory for temporarly saved values
    std::vector<Pulse *> tempValues;
    tempValues.resize(len);
    // start sorting 2 elements each time, then merge them with the two next to them etc
    for(unsigned int step=2; step/2 < len; step*=2)
    {
       for(unsigned int i=0; i < len; i+=step)
       {
          unsigned int endOfT2 = i+step;
          if(i+ step/2 >= len)
          {
             continue;
          }
          else if (i+step >=len)
          {
             endOfT2 = len;
          }
          // both sets have step/2 items.
          // t1 points to the first set of values
          unsigned int t1 = i;
          // t2 points to the second set of values
          unsigned int t2 = i+step/2;
          // here we save all the values that have been overridden from the first set
          unsigned int tempIndex=0;
          while(t1 < i+step/2 && t2 < endOfT2)
          {
             if(m_pulses[t1]->m_origin[1]>m_pulses[t2]->m_origin[1])
             {
                tempValues[tempIndex]=m_pulses[t1];
                t1++;
             }
             else
             {
                tempValues[tempIndex]=m_pulses[t2];
                t2++;
             }
             tempIndex++;
          }
          while(t1<i+step/2)
          {
             tempValues[tempIndex]=m_pulses[t1];
             t1++;
             tempIndex++;
          }
          // write values back to the array
          for(unsigned int t=0; t < tempIndex; ++t)
          {
              m_pulses[i+t]=tempValues[t];
          }
       }
    }
}


//-----------------------------------------------------------------------------
PulseManager::~PulseManager()
{
   for(unsigned int i=0; i<m_pulses.size(); ++i)
   {
      delete m_pulses[i];
   }
   m_discreteIntensities.resize(0);
   m_discretePoints.resize(0);
   m_pulses.resize(0);
}
