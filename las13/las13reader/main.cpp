#include "Las1_3_handler.h"
#include <iostream>
#include <fstream>

int main(void)
{
   std::cout.precision(10);
   //Las1_3_handler lasHandler("/users/rsg/mark1/scratch_space/EUFAR/testscripts/LDR-FW-FW10_01-2010-098-01.LAS");
   Las1_3_handler lasHandler("/users/rsg/arsf/arsf_data/2014/flight_data/uk/RG12_09-2014_172_Wessex/delivery/RG12_09-172-lidar-20140923/flightlines/fw_laser/las1.3/LDR-FW-RG12_09-2014-172-01.LAS");

   PulseManager *p = lasHandler.GetPointsWithClassification(7);
//   PulseManager *p = lasHandler.GetPointsInBounds(103000.0,102995.0,432915.0,432920.0);
   std::cout << "the pulse manager has : " << p->getNumOfPulses() << " pulses\n";

//   Pulse* pulse=p->getPulse(0);
//   if(pulse!=NULL)
//   {
//      std::cout<<pulse->originXYZ().size()<<std::endl;
//      std::cout<<" "<<pulse->originXYZ()[0]<<" "<<pulse->originXYZ()[1]<<" "<<pulse->originXYZ()[2]<<std::endl; 
//   }

//   PulseManager *p =NULL;
//   int npulses=0;
//   for(int loop=0;loop<20;loop++)
//   {
//      p=lasHandler.ReadLikeBook(1000000);
//      if(p!=NULL)   
//      {
//         npulses=p->getNumOfPulses();
//         std::cout <<"iteration "<<loop << "the pulse manager has : " << npulses << " pulses\n";
//      }
//   }
   //p->printPulseInfo(0);  
   lasHandler.DeletePulseManagers();
   return 0;
}
