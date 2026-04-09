// Params
Nwallcyly = 50; Rwallcyly = 0.98; 
Ntailx = 70; Rtailx = 0.99;
Ntaily = 70; Rtaily = 1.0; Rbump = 0.3;
NBLx = Ntaily; RBLx = 1.0;
NBLy = 12; RBLy = 0.85;

// Boundary points
Point(1) = {0, 0, 0, 1.0};
Point(2) = {16, 0, 0, 1.0};
Point(3) = {36, 0, 0, 1.0};
Point(4) = {36, 16, 0, 1.0};
Point(5) = {16, 16, 0, 1.0};
Point(6) = {0, 16, 0, 1.0};
// Cylinder points
Point(7) = {8, 8, 0, 1.0};
Point(8) = {8.70710678, 8.70710678, 0, 1.0};
Point(9) = {7.29289322, 8.70710678, 0, 1.0};
Point(10) = {7.29289322, 7.29289322, 0, 1.0};
Point(11) = {8.70710678, 7.29289322, 0, 1.0};
// BL Cylinder points
Point(12) = {9, 9, 0, 1.0};
Point(13) = {7, 9, 0, 1.0};
Point(14) = {7, 7, 0, 1.0};
Point(15) = {9, 7, 0, 1.0};
//
Line(1) = {1, 2}; Transfinite Curve {1} = Ntaily Using Bump 1/Rtaily;
Line(2) = {2, 3}; Transfinite Curve {2} = Ntailx Using Progression 1/Rtailx;
Line(3) = {6, 5}; Transfinite Curve {3} = Ntaily Using Bump 1/Rtaily;
Line(4) = {5, 4}; Transfinite Curve {4} = Ntailx Using Progression 1/Rtailx;
Line(5) = {1, 6}; Transfinite Curve {5} = Ntaily Using Bump 1/Rtaily;
Line(6) = {2, 5}; Transfinite Curve {6} = Ntaily Using Bump 1/Rbump;
Line(7) = {3, 4}; Transfinite Curve {7} = Ntaily Using Bump 1/Rbump;
// Cylinder curves
Circle(8) = {10, 7, 11}; Transfinite Curve {8} = Ntaily Using Progression Rtaily;
Circle(9) = {11, 7, 8}; Transfinite Curve {9} = Ntaily Using Bump 1/Rtaily;
Circle(10) = {8, 7, 9}; Transfinite Curve {10} = Ntaily Using Progression 1/Rtaily;
Circle(11) = {9, 7, 10}; Transfinite Curve {11} = Ntaily Using Bump 1/Rtaily;
// Block lines
Line(12) = {1, 14}; Transfinite Curve {12} = Nwallcyly Using Progression Rwallcyly;
Line(13) = {2, 15}; Transfinite Curve {13} = Nwallcyly Using Progression Rwallcyly;
Line(14) = {5, 12}; Transfinite Curve {14} = Nwallcyly Using Progression Rwallcyly;
Line(15) = {6, 13}; Transfinite Curve {15} = Nwallcyly Using Progression Rwallcyly;
// BL Cylinder curves
Circle(16) = {14, 7, 15}; Transfinite Curve {16} = NBLx Using Progression RBLx;
Circle(17) = {15, 7, 12}; Transfinite Curve {17} = NBLx Using Bump 1/RBLx;
Circle(18) = {12, 7, 13}; Transfinite Curve {18} = NBLx Using Progression 1/RBLx;
Circle(19) = {13, 7, 14}; Transfinite Curve {19} = NBLx Using Bump 1/RBLx;
// BL Block lines
Line(20) = {10, 14}; Transfinite Curve {20} = NBLy Using Progression 1/RBLy;
Line(21) = {11, 15}; Transfinite Curve {21} = NBLy Using Progression 1/RBLy;
Line(22) = {8, 12}; Transfinite Curve {22} = NBLy Using Progression 1/RBLy;
Line(23) = {9, 13}; Transfinite Curve {23} = NBLy Using Progression 1/RBLy;

// Surfaces
Curve Loop(1) = {12, 16, -13, -1};
Plane Surface(1) = {1};
Curve Loop(2) = {13, 17, -14, -6};
Plane Surface(2) = {2};
Curve Loop(3) = {14, 18, -15, 3};
Plane Surface(3) = {3};
Curve Loop(4) = {15, 19, -12, 5};
Plane Surface(4) = {4};
Curve Loop(5) = {6, 4, -7, -2};
Plane Surface(5) = {5};
// Loop 1 (top-left quad)
Curve Loop(6) = {11, -19, -23, 20};
Plane Surface(6) = {6};
// Loop 2 (top-right quad)
Curve Loop(7) = {10, -18, -22, 23};
Plane Surface(7) = {7};
// Loop 3 (bottom-left quad)
Curve Loop(8) = {9, -17, -21, 22};
Plane Surface(8) = {8};
// Loop 4 (bottom-right quad)
Curve Loop(9) = {8, -16, -20, 21};
Plane Surface(9) = {9};
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {5};
Transfinite Surface {6};
Transfinite Surface {7};
Transfinite Surface {8};
Transfinite Surface {9};
Recombine Surface {1};
Recombine Surface {2};
Recombine Surface {3};
Recombine Surface {4};
Recombine Surface {5};
Recombine Surface {6};
Recombine Surface {7};
Recombine Surface {8};
Recombine Surface {9};

Extrude {0, 0, 1} {
  Surface{1}; Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8}; Surface{9};
  Layers{1};
  Recombine;
}
//+
Physical Surface("inlet", 222) = {110};
//+
Physical Surface("outlet", 223) = {128};
//+
Physical Surface("topAndBottom", 224) = {88, 124, 44, 132};
//+
Physical Surface("cylinder", 225) = {164, 142, 208, 186};
//+
Physical Surface("frontAndBack", 226) = {4, 1, 45, 111, 89, 3, 67, 2, 199, 8, 177, 7, 6, 155, 9, 221, 5, 133};
//+
Physical Volume("volume", 227) = {4, 6, 7, 8, 9, 3, 2, 1, 5};
