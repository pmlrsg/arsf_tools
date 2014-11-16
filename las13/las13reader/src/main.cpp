#include "Las1_3_handler.h"
#include <iostream>
#include <fstream>

//This is a test program intended to be edited by you before compiling
//There is no command line testing etc 
//Note you need to pass a LAS1.3 file as first argument

int main (int argc, char const* argv[])
{
   try
   {
      std::cout.precision(10);
      std::string filename=argv[1];
      Las1_3_handler lasHandler(filename);

      PulseManager *p = lasHandler.GetPointsWithClassification(1);
   //   PulseManager *p = lasHandler.GetPointsInBounds(103000.0,102995.0,432915.0,432920.0);
      std::cout << "the pulse manager has : " << p->getNumOfPulses() << " pulses\n";

      Pulse* pulse=(*p)[0];
      if(pulse!=NULL)
      {
         //std::cout<<pulse->originXYZ().size()<<std::endl;
         std::cout<<" "<<pulse->sampleXYZ(0)[0]<<" "<<pulse->sampleXYZ(0)[1]<<" "<<pulse->sampleXYZ(0)[2]<<std::endl; 
         std::cout<<" "<<pulse->sampleXYZ(255)[0]<<" "<<pulse->sampleXYZ(255)[1]<<" "<<pulse->sampleXYZ(255)[2]<<std::endl; 
         std::cout<<" "<<std::endl;
         (*p)[2]->print();
      }

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
   }
   catch(std::string e)
   {
      std::cout<<e<<std::endl;
   }
   return 0;
}
