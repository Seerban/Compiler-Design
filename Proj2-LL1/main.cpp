#include <iostream>
#include <string>

std::string input = "vd$";
std::string output = "";
char next = input[0];
int idx = 0;

bool S(); bool A(); bool B(); bool C(); bool D(); bool E(); 

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
   if( std::string("av").find(next) != std::string::npos ) {
      if( !A() ) return false;
      if( !B() ) return false;
      return true;
   }
   else if( std::string("c").find(next) != std::string::npos ) {
      if( !C() ) return false;
      if( !D() ) return false;
      return true;
   }
   else if( next == 'b' ) {
      if( !read('b') ) return false;
      return true;
   }
   return false; // ERROR
}

bool A() {
   output += "A";
   std::cout<<"A"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( next == 'a' ) {
      if( !read('a') ) return false;
      if( !A() ) return false;
      return true;
   }
   else if( next == 'v' ) {
      if( !read('v') ) return false;
      return true;
   }
   return true; // NULLABLE
}

bool B() {
   output += "B";
   std::cout<<"B"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( std::string("c").find(next) != std::string::npos ) {
      if( !C() ) return false;
      if( !B() ) return false;
      return true;
   }
   else if( next == 'd' ) {
      if( !read('d') ) return false;
      return true;
   }
   return false; // ERROR
}

bool C() {
   output += "C";
   std::cout<<"C"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( next == 'c' ) {
      if( !read('c') ) return false;
      return true;
   }
   return true; // NULLABLE
}

bool D() {
   output += "D";
   std::cout<<"D"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( std::string("gf").find(next) != std::string::npos ) {
      if( !E() ) return false;
      if( !A() ) return false;
      return true;
   }
   else if( next == 'a' ) {
      if( !read('a') ) return false;
      return true;
   }
   return false; // ERROR
}

bool E() {
   output += "E";
   std::cout<<"E"<<"-"<<"char:"<<next<<"-"<<"idx:"<<idx<<"\n";
   if( next == 'f' ) {
      if( !read('f') ) return false;
      if( !E() ) return false;
      return true;
   }
   else if( next == 'g' ) {
      if( !read('g') ) return false;
      return true;
   }
   return false; // ERROR
}

int main() {
   bool fin = S();
   std::cout<<output;
   std::cout<<"\n"<<"finalizat = "<<fin<<"\n";}