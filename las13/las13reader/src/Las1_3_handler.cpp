#include "Las1_3_handler.h"
#include <cstdio>
#include <cstdlib>
#include <vector>
#include <cstring>
#include <string>
#include <algorithm>
#include <new>
#include <iomanip>
#include <iostream>
#include <fstream>

//-----------------------------------------------------------------------------
// Constructor - open las file and set up parameters
//-----------------------------------------------------------------------------
Las1_3_handler::Las1_3_handler(
        std::string i_filename
        ): m_filename(i_filename),i_hist(0)
{   
   //Open the lasfile here and read in the header information
   lasfile.open(m_filename.c_str(),std::ios::binary | std::ios::in);
   if(!lasfile.is_open())
   {
      std::cerr << "File failed to open. \n";
      return;
   }
   //Get the filesize
   lasfile.seekg(0,lasfile.end);
   filesize=lasfile.tellg();
   lasfile.seekg(0,lasfile.beg);

   //Read the headers
   read_public_header();
   read_variable_length_records();
   //Don't have wild pointers
   pmanager_book=NULL;
   //empty the pulsemanagervector 
   pulsemanagervector.clear();
   quiet=false;
}

//-----------------------------------------------------------------------------
// Common code to create a new pulse manager 
//-----------------------------------------------------------------------------
PulseManager* Las1_3_handler::NewPulseManager()
{
   PulseManager* i_pulseManager = new (std::nothrow) PulseManager(public_header,wv_info);
   if(i_pulseManager==0)
   {
       std::cerr << "Error: Memory could not be allocated\n";
       return NULL;
   }
   //add the pulse manager pointer to the vector to keep track of them
   pulsemanagervector.push_back(i_pulseManager);
   return i_pulseManager;
}

//-----------------------------------------------------------------------------
// Common code to read a point into a point record struct
//-----------------------------------------------------------------------------
bool Las1_3_handler::ReadPoint(Types::Data_Point_Record_Format_4* point_info)
{
   //Read in a point if lasfile is good
   if((lasfile.good())&&((unsigned)lasfile.tellg() < public_header.start_of_wf_data_Packet_record))
   {
      lasfile.read((char *) point_info, (int) public_header.point_data_record_length);
   }
   else if((unsigned)lasfile.tellg() >= public_header.start_of_wf_data_Packet_record)
   {
      //End of point section
      return false;
   }
   else
   {
      perror("Error reading point: ");
      if(lasfile.eof())
         std::cout<<"LAS file reader at end of file at position: "<<std::endl;
      else if(lasfile.bad())
         std::cout<<"LAS file reader stream is bad:"<<std::endl;
      else if(lasfile.fail())
         std::cout<<"LAS file reader stream has failed."<<std::endl;
      return false;
   }
   return true;
}

//-----------------------------------------------------------------------------
// Function to return the same pulse manager each time it is 
// called reading the next set of points
//-----------------------------------------------------------------------------
PulseManager* Las1_3_handler::ReadLikeBook(unsigned int chunksize,bool resettostart)
{
   Types::Data_Point_Record_Format_4 point_info;
   //If requested then reset the pointer to the start of the point records
   if((resettostart==true)||(pmanager_book==NULL))
   {
      lasfile.clear();
      lasfile.seekg((int) public_header.offset_to_point,std::ios::beg);
   }

   //Check if file pointer is past the number of point records (before fw block)
   //if so - return a null pointer
   if((unsigned)lasfile.tellg() > public_header.start_of_wf_data_Packet_record)
   {
      //Will not error in case user wants to use the null pointer to (assume) reader is
      //at the end of the file
      return NULL;
   }

   //clean up and create a new pulse manager
   if(pmanager_book!=NULL)
      delete pmanager_book;
   pmanager_book=new (std::nothrow) PulseManager(public_header,wv_info);

   unsigned int count=0;
   unsigned int countDiscrete = 0;
   unsigned int countIgnored = 0;
   // temporarly saving discrete values that are associated with a
   // waveform but the 1st return haven't been saved yet
   std::vector<Vec3d> discretePoints;
   // the corresponding intensities of the discrete points
   std::vector<unsigned short> discreteIntensities;
   // the corresponding wave offsets of the dicrete points
   std::vector<int> discreteWaveOffsets;
   // the corresponding offset in the waveform
   std::vector<double> discretePointInWaveform;

   //For each point in the chunksize
   for(unsigned int i=0;i<chunksize;i++)
   {
      if(!ReadPoint(&point_info))
      {
         continue;
      }
      //Handle the point
      HandlePoint(point_info,count,pmanager_book,discretePoints,discreteIntensities,discreteWaveOffsets,
                  discretePointInWaveform,countDiscrete,countIgnored);
   }
   //Try and sort out the discrete points
   pmanager_book->sortDiscretePoints(discretePoints,discreteIntensities,discreteWaveOffsets,discretePointInWaveform);

   return pmanager_book;
}

//-----------------------------------------------------------------------------
// Function to return a pulse manager containing points within the given bounds
//-----------------------------------------------------------------------------
PulseManager* Las1_3_handler::GetPointsInBounds(float boundsn,float boundss,float boundsw,float boundse)
{
   //Set up the new pulse manager
   PulseManager* i_pulseManager=NewPulseManager();
   Types::Data_Point_Record_Format_4 point_info;

   //Seek to start of point data
   lasfile.seekg((int) public_header.offset_to_point,std::ios::beg);

   unsigned int count=0;
   unsigned int countDiscrete = 0;
   unsigned int countIgnored = 0;
   // temporarly saving discrete values that are associated with a
   // waveform but the 1st return haven't been saved yet
   std::vector<Vec3d> discretePoints;
   // the corresponding intensities of the discrete points
   std::vector<unsigned short> discreteIntensities;
   // the corresponding wave offsets of the dicrete points
   std::vector<int> discreteWaveOffsets;
   std::vector<double> discretePointInWaveform;

   if((boundsn < boundss)||(boundse < boundsw))
   {
      std::cout<<"Bounds should be [N, S, W, E]. I got: "<<boundsn <<" "<< boundss<<" "<<boundsw<<" "<<boundse<<std::endl;
      return NULL;
   }
      
   for(unsigned int i=0; i< public_header.number_of_point_records; ++i)
   {
      if(!ReadPoint(&point_info))
         continue;

      //Get the point x,y position
      float pointx=point_info.X*public_header.x_scale_factor + public_header.x_offset;
      float pointy=point_info.Y*public_header.y_scale_factor + public_header.y_offset;
      //if the point is within the bounds
      if((pointx<boundse)&&(pointx>boundsw)&&(pointy<boundsn)&&(pointy > boundss))
      {
         HandlePoint(point_info,count,i_pulseManager,discretePoints,discreteIntensities,discreteWaveOffsets,discretePointInWaveform,countDiscrete,countIgnored);
      }
   }
   if(!quiet)
   {
      if(count==0)
      {
          std::cout << "no waveforms associated with that area\n";
      }
      else
      {
          std::cout << count << " waveforms found\n";
          std::cout << countDiscrete << " additional discrete points found\n";
          std::cout << countIgnored << " discrete points ignored (bad wave form pointer)\n";
      }
   }

   i_pulseManager->sortDiscretePoints(discretePoints,discreteIntensities,discreteWaveOffsets,discretePointInWaveform);

   //clear any flags from the reader
   lasfile.clear();

   return i_pulseManager;
}

//-----------------------------------------------------------------------------
// Function to get points with a given classification value
//-----------------------------------------------------------------------------
PulseManager* Las1_3_handler::GetPointsWithClassification(int classvalue)
{
   //Set up the new pulse manager
   PulseManager* i_pulseManager=NewPulseManager();

   //Seek to start of point data
   lasfile.seekg((int) public_header.offset_to_point,std::ios::beg);
   Types::Data_Point_Record_Format_4 point_info;

   unsigned int count=0;
   unsigned int countDiscrete = 0;
   unsigned int countIgnored = 0;
   // temporarly saving discrete values that are associated with a
   // waveform but the 1st return haven't been saved yet
   std::vector<Vec3d> discretePoints;
   // the corresponding intensities of the discrete points
   std::vector<unsigned short> discreteIntensities;
   // the corresponding wave offsets of the dicrete points
   std::vector<int> discreteWaveOffsets;
   // the corresponding offset in the waveform
   std::vector<double> discretePointInWaveform;

   //if -ve class value then will get all points
   if(classvalue < 0)
   {
      if(!quiet)
         std::cout<<"Given class value is negative - will return all points"<<std::endl;
   }
      
   for(unsigned int i=0; i< public_header.number_of_point_records; ++i)
   {
      //Read in a point
      if(!ReadPoint(&point_info))
         continue;

      //If the point has the classification specified
      if(((int)point_info.classification==classvalue)||(classvalue < 0))
      {
         HandlePoint(point_info,count,i_pulseManager,discretePoints,discreteIntensities,discreteWaveOffsets,discretePointInWaveform,countDiscrete,countIgnored);
      }
   }

   if(!quiet)
   {
      if(count==0)
      {
          std::cout << "no waveforms associated with that area\n";
      }
      else
      {
          std::cout << count << " waveforms found\n";
          std::cout << countDiscrete << " extra discrete points found\n";
          std::cout << countIgnored << " discrete points ignored (bad wave form pointer)\n";
      }
   }

   i_pulseManager->sortDiscretePoints(
               discretePoints,discreteIntensities,discreteWaveOffsets,discretePointInWaveform);

   //clear any flags from the reader
   lasfile.clear();
   return i_pulseManager;
}

//Function to handle the points (used in pulseManager returning functions)
void Las1_3_handler::HandlePoint(Types::Data_Point_Record_Format_4& point_info,unsigned int& count,
                  PulseManager* i_pulseManager,std::vector<Vec3d>& discretePoints,std::vector<unsigned short>&  discreteIntensities,
                  std::vector<int>& discreteWaveOffsets,std::vector<double>& discretePointInWaveform,unsigned int& countDiscrete,unsigned int& countIgnored)
{   
   //Get the wave offset
   unsigned int wave_offset = public_header.start_of_wf_data_Packet_record + point_info.byte_offset_to_wf_packet_data;
   //Need to check for sensible wave_offset values - i.e. less than filesize - 1 wave packet 
   if(wave_offset >= (filesize-point_info.wf_packet_size_in_bytes))
   {
      countIgnored++;      
      return;
   }

   if( point_info.wave_packet_descriptor_index!=0 && (unsigned int)(point_info.returnNo_noOfRe_scanDirFla_EdgeFLn&7)==1 )
   {
      count++;
      char *wave_data = new (std::nothrow) char [point_info.wf_packet_size_in_bytes];
      if(wave_data==0)
      {
         std::cerr << "Fail assigning memory in file Las1_3_handler.cpp\n";
         return;
      }
      std::streampos curpos = lasfile.tellg();
      lasfile.seekg(wave_offset);
      lasfile.read((char *) wave_data,point_info.wf_packet_size_in_bytes);
      i_pulseManager->addPoint(point_info,wave_data,wave_offset);
      lasfile.seekg(curpos);
      delete []wave_data;
   }
   else if (point_info.wave_packet_descriptor_index!=0)
   {
      // temporarly save point
      Vec3d dpoint(point_info.X*public_header.x_scale_factor,
                               point_info.Y*public_header.y_scale_factor,
                               point_info.Z*public_header.z_scale_factor);
      discretePoints.push_back(dpoint);
      discreteIntensities.push_back(point_info.itensity);
      discreteWaveOffsets.push_back(wave_offset);
      discretePointInWaveform.push_back(point_info.return_point_wf_location);

      countDiscrete++;
      // no waveform associated with the data
   }
   else
   {
      countDiscrete++;
      i_pulseManager->addUnAssociatedDiscretePoint(point_info);
   }
}

//-----------------------------------------------------------------------------
void Las1_3_handler::read_public_header()
{
   //Note this assumes that you are at the start of the file
   //is called in constructor and should not be called again
   lasfile.read((char *) &public_header,sizeof(public_header));

   //Do not know why these have been fabs'ed so commenting out
   //public_header.x_offset = fabs(public_header.x_offset);
   //public_header.y_offset = fabs(public_header.y_offset);
   //public_header.z_offset = fabs(public_header.z_offset);

   // tests if waveform data packets are saved into that file
   // if not program terminates because it cannot handle that case
   if((public_header.global_encoding & 2 ) !=2 )
   {
      std::cerr << "Waveform Data Packets are not saved in this file.\n";
      return;
   }

   // test version of the file. version should be 1.3
   if (public_header.version_major!=1 || public_header.version_minor!=3)
   {
      std::cerr << "Incorrect version. Only LAS 1.3 is allowed.\n";
      return;
  }
}

//-----------------------------------------------------------------------------
void Las1_3_handler::read_variable_length_records()
{
   Types::Variable_Length_Record_Header headdata_rec;
   for(unsigned int i=0; i<public_header.number_of_variable_lenght_records;
      ++i)
   {
      lasfile.read((char *) &headdata_rec, VbleRec_header_length);
      char skip_record [headdata_rec.record_length_after_header];
      lasfile.read((char *) skip_record,headdata_rec.record_length_after_header);

      // 1001 for the intensity histogram
      /*
      #If RecordID= 1001 it is the intensity histogram
      # of 1st returns w/ intensity of 0
      # of 1st returns w/ intensity of 1
      # of 1st returns w/ intensity of 2
      #
      # of 1st returns w/ intensity of 255
      # of 2nd returns w/ intensity of 0
      # of 2nd returns w/ intensity of 1
      # of 2nd returns w/ intensity of 2
      #
      # of 2nd returns w/ intensity of 255
      # of 3rd returns w/ intensity of 0
      # of 3rd returns w/ intensity of 1
      # of 3rd returns w/ intensity of 2
      #
      # of 3rd returns w/ intensity of 255
      # of returns with AGC value of 0
      # of returns with AGC value of 1
      # of returns with AGC value of 2
      #
      # of returns with AGC value of 255
      # of all returns with intensity of 0
      # of all returns with intensity of 1
      # of all returns with intensity of 2
      #
      # of all returns with intensity of 255
      */
      if(headdata_rec.record_ID == 1001)
      {
         i_hist = new (std::nothrow) int[headdata_rec.record_length_after_header/4];
         if(i_hist==0)
         {
             std::cout << "Memory assignment failed in Las1_3_handler\n";
             return;
         }
         memcpy((void *)i_hist,(void *)skip_record,headdata_rec.record_length_after_header);
      }

      // 1002 for Leica mission info containing
      /*
      #If RecordID= 1002 it is Leica mission info containing
      #0_ Laser Pulserate: 1 Hz
      #1_ Field Of View: 0.1 degrees
      #2_ Scanner Offset: 1 ticks
      #3_ Scan Rate:  0.1 Hz
      #4_ Flying Altitude (AGL): meters
      #5_ GPS Week Number at start of line:   week
      #6_ GPS Seconds of Week at start of line: seconds
      #7_ Reserved
      #NOTE Leica definition says this record contains 26 bytes but it actually contains only 22 so not sure what is what...
      # By comparisson with FlightLineLog fields 0,3,4,5 and 6 are ok
      */
      else if (headdata_rec.record_ID == 1002)
      {
         memcpy((void *) &mis_info,(void *)skip_record,sizeof(mis_info));
      }
      else if (headdata_rec.record_ID == 1003)
      {

      }
      else if (headdata_rec.record_ID>=100 && headdata_rec.record_ID<356)
      {
         memcpy((void *) &wv_info, (void *) skip_record, sizeof(wv_info));
      }
   }
}

//-----------------------------------------------------------------------------
void Las1_3_handler::printPublicHeader()const
{
   std::cout << std::setprecision(2) << std::fixed;
   std::cout << "\nHeader file of " << m_filename << std::endl;
   std::cout << "File Signature " << public_header.file_signiture << std::endl;
   std::cout << "File Source ID  "<< public_header.file_source_ID << std::endl;
   std::cout << "Global Encoding "<< public_header.global_encoding << std::endl;
   std::cout << "Project ID - GUID data 1 " << public_header.project_ID_GUID_data_1 << std::endl;
   std::cout << "Project ID - GUID data 2 " << public_header.project_ID_GUID_data_2 << std::endl;
   std::cout << "Project ID - GUID data 3 " << public_header.project_ID_GUID_data_3 << std::endl;
   std::cout << "Project ID - GUID data 4 " << public_header.project_ID_GUID_data_4 << std::endl;
   std::cout << "Version Major " << (int) public_header.version_major << std::endl;
   std::cout << "Version Minor " << (int) public_header.version_minor << std::endl;
   std::cout << "System Identifier " << public_header.system_identifier << std::endl;
   std::cout << "Generating Software " << public_header.generating_software << std::endl;
   std::cout << "File Creation Day of Year  " << public_header.file_creation_day_of_year << std::endl;
   std::cout << "File Creation Year " << public_header.file_creation_year << std::endl;
   std::cout << "Header Size    "  <<  public_header.header_size << std::endl;
   std::cout << "Offset to point data "  <<  public_header.offset_to_point << std::endl;
   std::cout << "Number of Variable Length Records "  <<  public_header.number_of_variable_lenght_records << std::endl;
   std::cout << "Point Data Format ID (0-99 for spec) "  << (int)  public_header.point_data_format_ID << std::endl;
   std::cout << "Point Data Record Length "  <<  public_header.point_data_record_length << std::endl;
   std::cout << "Number of point records " <<  public_header.number_of_point_records << std::endl;
   std::cout << "Number of points by return  " <<  public_header.number_of_points_by_return[0] << " "
             <<  public_header.number_of_points_by_return[1]<< " "
             <<  public_header.number_of_points_by_return[2]<< " "
             <<  public_header.number_of_points_by_return[3]<< " "
             <<  public_header.number_of_points_by_return[4]  <<  std::endl;
   std::cout << "X scale factor "  <<  public_header.x_scale_factor << std::endl;
   std::cout << "Y scale factor  "  <<  public_header.y_scale_factor << std::endl;
   std::cout << "Z scale factor "  <<  public_header.z_scale_factor << std::endl;
   std::cout << "X offset  "  <<  (double) public_header.x_offset << std::endl;
   std::cout << "Y offset  " <<  (double) public_header.y_offset << std::endl;
   std::cout << "Z offset "  <<  (double) public_header.z_offset << std::endl;
   std::cout << "Max X  "  << (double) public_header.max_x << std::endl;
   std::cout << "Min X  "  << (double)  public_header.min_x << std::endl;
   std::cout << "Max Y  " <<  (double) public_header.max_y << std::endl;
   std::cout << "Min Y " <<  (double) public_header.min_y << std::endl;
   std::cout << "Max Z  " <<  (double) public_header.max_z << std::endl;
   std::cout << "Min Z  " <<  (double) public_header.min_z << std::endl;
   std::cout << "Start of Waveform Data Packet Record " <<  public_header.start_of_wf_data_Packet_record << std::endl;
}

//-----------------------------------------------------------------------------
Las1_3_handler::~Las1_3_handler()
{
   if (i_hist!=0)
   {
      delete []i_hist;
   }
   //close the lasfile
   lasfile.close();
   lasfile.clear();
   //tidy up any pulse managers still open
   DeletePulseManagers();

   if(pmanager_book!=NULL)
      delete pmanager_book;
}

