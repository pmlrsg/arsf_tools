#ifndef TYPES_H
#define TYPES_H

class Types
{

public:
    // use pragma to align struct in order to pack data together
    // 240 bytes used instead of 235 if #pragma is not used to pack data together
#pragma pack(push)
#pragma pack(1)
   typedef struct Public_Header_Block                    //235 bytes
   {
      // ---------------------------------------------------------------
      // file signiture is always "LASF"
      // ---------------------------------------------------------------
      char file_signiture[4];                            //  4 bytes   0
      // ---------------------------------------------------------------
      // should be between 1-65535 and it could be the flight line number
      // 0 indicates that it haven't been specified
      // ---------------------------------------------------------------
      unsigned short file_source_ID;                     //  2 bytes   1
      // ---------------------------------------------------------------
      // global proberties about the file
      // this handler assumes that the waveform data packets are always internal
      // this means that they are saved in the same file and the second bit of
      // the global encoding is always set if not program terminates returning an error
      // ---------------------------------------------------------------
      unsigned short global_encoding;                    //  2 bytes   2
      // ---------------------------------------------------------------
      // optional
      // ---------------------------------------------------------------
      unsigned int project_ID_GUID_data_1;               //  4 bytes   3
      unsigned short project_ID_GUID_data_2;             //  2 bytes   4
      unsigned short project_ID_GUID_data_3;             //  2 bytes   5
      unsigned char project_ID_GUID_data_4 [8];          //  8 bytes   6
      // ---------------------------------------------------------------
      // version should always be 1.3
      // ---------------------------------------------------------------
      unsigned char version_major;                       //  1 bytes   7
      unsigned char version_minor;                       //  1 bytes   8
      char system_identifier [32];                       // 32 bytes   9
      char generating_software [32];                     // 32 bytes  10
      // ---------------------------------------------------------------
      // compute at the Greenwich Mean Time (GMT) day
      // with Jan 1 considered to be day 1
      // ---------------------------------------------------------------
      unsigned short file_creation_day_of_year;          //  2 bytes  11
      unsigned short file_creation_year;                 //  2 bytes  12
      // ---------------------------------------------------------------
      // always 235 unless more data are added to the end of the header
      // ---------------------------------------------------------------
      unsigned short header_size;                        //  2 bytes  13
      // ---------------------------------------------------------------
      // number of bytes from the beginning of the file
      // to the first field of the first point record data field
      // ---------------------------------------------------------------
      unsigned int offset_to_point;                      //  4 bytes  14
      unsigned int number_of_variable_lenght_records;    //  4 bytes  15
      unsigned char point_data_format_ID;                //  1 bytes  16
      // ---------------------------------------------------------------
      // the size of point data record in bytes
      // ---------------------------------------------------------------
      unsigned short point_data_record_length;           //  2 bytes  17
      unsigned int number_of_point_records;              //  4 bytes  18
      unsigned int number_of_points_by_return [5];       // 20 bytes  19:23
      // ---------------------------------------------------------------
      // these scale factors must be applied to each point x,y,z
      // ---------------------------------------------------------------
      double x_scale_factor;                             //  8 bytes  24
      double y_scale_factor;                             //  8 bytes  25
      double z_scale_factor;                             //  8 bytes  26
      // these offset must be added to each point x,y,z
      double x_offset;                                   //  8 bytes  27
      double y_offset;                                   //  8 bytes  28
      double z_offset;                                   //  8 bytes  29
      // max and min data fields
      double max_x;                                      //  8 bytes  30
      double min_x;                                      //  8 bytes  31
      double max_y;                                      //  8 bytes  32
      double min_y;                                      //  8 bytes  33
      double max_z;                                      //  8 bytes  34
      double min_z;                                      //  8 bytes  35
      // ---------------------------------------------------------------
      // the number of bytes from the beginning of the file to
      // the first byte of the waveform data Packet header
      // ---------------------------------------------------------------
      unsigned long long start_of_wf_data_Packet_record; //  8 bytes  36
   }Public_Header_Block;
#pragma pack(pop)


    //    VbleRec_head_format="=H16sHH32s"
    // Variable Length Record Header format
#pragma pack(push)
#pragma pack(1)
   typedef struct Variable_Length_Record_Header          // 54 bytes
   {
     unsigned short reserved;                            //  2 bytes   0
     char user_ID [16];                                  // 16 bytes   1
     unsigned short record_ID;                           //  2 bytes   2
     unsigned short record_length_after_header;          //  2 bytes   3
     char description [32];                              // 32 bytes   4
    }Variable_Length_Record_Header;
#pragma pack(pop)


    // point data format
#pragma pack(push)
#pragma pack(1)
   typedef struct Data_Point_Record_Format_4             // 57 bytes
   {
      int X;                                             //  4 bytes   0
      int Y;                                             //  4 bytes   1
      int Z;                                             //  4 bytes   2
      unsigned short itensity;                           //  2 bytes   3
      unsigned char returnNo_noOfRe_scanDirFla_EdgeFLn;  //  1 bytes   4
      // ---------------------------------------------------------------
      // 0:4 bits
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
      // 5th bit - Synthetic
      // ---------------------------------------------------------------
      // 6th bit - Key-Point: do not withheld in thinning algorithm
      // ---------------------------------------------------------------
      // 7th bit - Withheld: Deleted, do not include in processing
      // ---------------------------------------------------------------
      unsigned char classification;                      //  1 bytes   5
      // ---------------------------------------------------------------
      // in the range of -90 to +90
      // 0 for nadir and -90 to the left side of the aircraft in the
      // direction of the flight
      // ---------------------------------------------------------------
      char scan_angle_rank;                              //  1 bytes   6
      unsigned char user_data;                           //  2 bytes   7 8
      unsigned char gain;                                //
      unsigned char point_source_ID;                     //  1 bytes   9
      double GBS_time;                                   //  8 bytes   10
      // ---------------------------------------------------------------
      // LAS 1.3 supports up to 255 user definded records
      // 0 indicates no waveforms
      // ---------------------------------------------------------------
      unsigned char wave_packet_descriptor_index;        //  1 bytes  11
      // ---------------------------------------------------------------
      // absolute location of the beginning of the first waveform packet
      // relative to the beginning of the file is given by:
      // Start of WF data Packet Record + Byte offset to WF packet data
      // ---------------------------------------------------------------
      unsigned long long byte_offset_to_wf_packet_data;  //  8 bytes  12
      unsigned int wf_packet_size_in_bytes;              //  4 bytes  13
      float return_point_wf_location;                    //  4 bytes  14
      // ---------------------------------------------------------------
      // for extrapolating points along the waveform
      // X = X0 + X(t) , t=time in picoseconds
      // Y = Y0 + Y(t)
      // Z = Z0 + Z(t)
      // ---------------------------------------------------------------
      float X_t;                                         //  4 bytes  15
      float Y_t;                                         //  4 bytes  16
      float Z_t;                                         //  4 bytes  17
   }Data_Point_Record_Format_4;
#pragma pack(pop)



#pragma pack(push)
#pragma pack(1)
   typedef struct WF_packet_Descriptor                   //  26 bytes
   {
      unsigned char bits_per_sample;                     //   1 byte   0
      // ---------------------------------------------------------------
      // 0 is only currently supported - indicates no compression
      // ---------------------------------------------------------------
      unsigned char wf_compression_type;                 //   1 byte   1
      unsigned int number_of_samples;                    //   4 bytes  2
      // ---------------------------------------------------------------
      // 500 1000 2000 picoseconds represent 2GHz, 1GHz 500MHz respectively
      // ---------------------------------------------------------------
      unsigned int temporal_sample_spacing;              //   4 bytes  3
      double digitizer_gain;                             //   8 bytes  4
      double digitizer_offset;                           //   8 bytes  5
   }WF_packet_Descriptor;
#pragma pack(pop)


#pragma pack(push)
#pragma pack(1)
   typedef struct Leica_mission_info                         //   12 of 22 only used in python script
   {
      int laster_pulse_rate;                             //   4 bytes  0
      unsigned short int field_of_view;                      //   2 bytes  1
      unsigned short int scanner_offset;                     //   2 bytes  2
      short int scan_rate;                                   //   2 bytes  3
      short int fly_altitude;                                //   2 bytes  4
//      short
//      int
//      int
   }Leica_mission_info;
#pragma pack(pop)


};


#endif // TYPES_H
