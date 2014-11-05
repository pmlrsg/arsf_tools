#ifndef LAS1_3_HANDLER_H
#define LAS1_3_HANDLER_H

#include <iostream>
#include <fstream>
#include <string>

#include "Types.h"
#include "PulseManager.h"

/// @authors Milto Miltiadou, supported by the Centre for DIgital Entertainment at the University of Bath, and Plymouth Marine Laboratory
//The code is released under the GNU General Public License v3.0.
//It reads a LAS1.3 file under the LAS specification version 1.3-R11 released October 24, 2010 (Available at: http://www.asprs.org/a/society/committees/standards/LAS_1_3_r11.pdf), using only the Point Data Record Format 4.
//The original script was written in Python and it's available here: https://github.com/pmlrsg/arsf_tools and a lot of the comments were copied that Python script and the LAS1.3 file specifications

class Las1_3_handler
{
public:
   //-------------------------------------------------------------------------
   /// @brief default constructor
   /// @param[in] i_filename the file of the name to be read
   //-------------------------------------------------------------------------
   Las1_3_handler(std::string i_filename);

   //-------------------------------------------------------------------------
   /// @brief method that prints headdata
   //-------------------------------------------------------------------------
   void printPublicHeader()const;
   //-------------------------------------------------------------------------
   /// @brief default destructor
   //-------------------------------------------------------------------------
   ~Las1_3_handler();

   //-------------------------------------------------------------------------
   //Function to only return points of certain classification
   //-------------------------------------------------------------------------
   PulseManager* GetPointsWithClassification(int classvalue);

   //-------------------------------------------------------------------------
   //Function to only return points contained in certain bounds
   //-------------------------------------------------------------------------
   PulseManager* GetPointsInBounds(float boundsn,float boundss,float boundsw,float boundse);

   //-------------------------------------------------------------------------   
   //Delete (free memory) from PulseManagers
   //-------------------------------------------------------------------------
   void DeletePulseManagers()
   {
      for(std::vector<PulseManager*>::iterator it=pulsemanagervector.begin();it!=pulsemanagervector.end();it++) 
      {
         if(*it != NULL)
            delete *it;
      } 
      pulsemanagervector.clear();
   }

   //-------------------------------------------------------------------------
   //-------------------------------------------------------------------------
   PulseManager* ReadLikeBook(unsigned int chunksize=1,bool resettostart=false);

   void SetQuiet(bool q){quiet=q;}

protected:
   //-------------------------------------------------------------------------
   /// @brief the name of the LAS file
   //-------------------------------------------------------------------------
   std::string m_filename;
   //-------------------------------------------------------------------------
   /// @brief the publi header block of the LAS1.3 file
   //-------------------------------------------------------------------------
   Types::Public_Header_Block public_header;
   //-------------------------------------------------------------------------
   /// @brief the intensity histogram of the lasfile
   //-------------------------------------------------------------------------
   int *i_hist;
   //-------------------------------------------------------------------------
   /// @brief Leica mission information
   //-------------------------------------------------------------------------
   Types::Leica_mission_info mis_info;
   //-------------------------------------------------------------------------
   /// @brief waveform packet descriptor
   //-------------------------------------------------------------------------
   Types::WF_packet_Descriptor wv_info;

private:
   //-------------------------------------------------------------------------
   /// @brief method that reads public header block
   //-------------------------------------------------------------------------
   void read_public_header();
   //-------------------------------------------------------------------------
   /// @brief method that reads variable length records including waveform
   /// packet descriptors (up to 255)
   //-------------------------------------------------------------------------
   void read_variable_length_records();
   //-------------------------------------------------------------------------
   /// @brief saved here to avoid opening and closing the file multiple times
   //-------------------------------------------------------------------------
   std::ifstream lasfile;
   //-------------------------------------------------------------------------
   /// @brief Public Header length in bytes.
   //-------------------------------------------------------------------------
   static const unsigned int public_header_length = 235;
   //-------------------------------------------------------------------------
   /// @brief  Variable Length Record Header length in bytes
   //-------------------------------------------------------------------------
   static const unsigned int VbleRec_header_length = 54;
   //-------------------------------------------------------------------------
   /// @brief Extended Variable Lenght Record Header, in Version 1.3 the only
   /// EVLR is waveform data packets
   //-------------------------------------------------------------------------
   static const unsigned int EVLR_length = 60;
   //-------------------------------------------------------------------------
   /// @brief the length of the point data
   //-------------------------------------------------------------------------
   static const unsigned int point_data_length = 57;

   //-------------------------------------------------------------------------
   // @brief Common code for handling points in GetPointsWith functions
   //-------------------------------------------------------------------------
   void HandlePoint(Types::Data_Point_Record_Format_4& point_info,unsigned int& count,
                  PulseManager* i_pulseManager,std::vector<Vec3d>& discretePoints,std::vector<unsigned short>&  discreteIntensities,
                  std::vector<int>& discreteWaveOffsets,std::vector<double>& discretePointInWaveform,
                  unsigned int& countDiscrete,unsigned int& countIgnored);

   //-------------------------------------------------------------------------
   // @brief Vector to store pointers to all pulsemanagers created so that can be cleaned up afterwards
   //-------------------------------------------------------------------------
   std::vector<PulseManager*> pulsemanagervector;

   //-------------------------------------------------------------------------
   /// @brief a pulsemanager pointer to use for the ReadLikeBook function
   //-------------------------------------------------------------------------
   PulseManager* pmanager_book;

   //-------------------------------------------------------------------------
   /// @brief the length of the LAS file in bytes
   //-------------------------------------------------------------------------
   uint64_t filesize;

   //-----------------------------------------------------------------------------
   // @brief Common code to create a new pulse manager
   //-----------------------------------------------------------------------------  
   PulseManager* NewPulseManager();

   //-----------------------------------------------------------------------------
   // @brief Common code to read a point into a point record struct
   //-----------------------------------------------------------------------------
   bool ReadPoint(Types::Data_Point_Record_Format_4* point_info);

   //-----------------------------------------------------------------------------
   // @brief tell the library to be quiet - do not print status messages
   //-----------------------------------------------------------------------------   
   bool quiet;
};

#endif // LAS1_3_HANDLER_H
