#include <iostream>
#include <string>

std::string input = "aavccdd$";
std::string output = "";
char next = input[0];
int idx = 0;

bool S(); bool A(); bool B(); 

bool read(char c) {
   if( c == next ) {
   std::cout<<"reading char "<<c<<"\n";
      idx++;
      next = input[idx];
      return true;
   }
   return false;
};

bool S() {
   output += "S";
   std::cout<<"S"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( next == 'a' ) {
      if( !read('a') ) return false;
      if( !A() ) return false;
      return true;
   }
   return false; // ERROR
}

bool A() {
   output += "A";
   std::cout<<"A"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( next == 'b' ) {
      if( !read('b') ) return false;
      if( !B() ) return false;
      return true;
   }
   return false; // ERROR
}

bool B() {
   output += "B";
   std::cout<<"B"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   return false; // ERROR
}

int main() {
   bool fin = S();
   std::cout<<output;
   std::cout<<"\n"<<"finalizat = "<<fin<<" pentru inputul "<<input<<"\n";}