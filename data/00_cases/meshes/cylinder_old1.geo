// Params
Nx1 = 41; Rx1 = 1.00;
Nx2 = 41; Rx2 = 1.00;
Ny  = 41; Ry  = 5.00;
Nb  = 41; Rb  = 0.90;
Nc  = 41; Rc  = 1.00;

// Boundary points
Point(1) = {0, 0, 0, 1.0};
Point(2) = {16, 0, 0, 1.0};
Point(3) = {40, 0, 0, 1.0};
Point(4) = {40, 20, 0, 1.0};
Point(5) = {16, 20, 0, 1.0};
Point(6) = {0, 20, 0, 1.0};
// Cylinder points
Point(7) = {8, 10, 0, 1.0};
Point(8) = {8.70710678, 10.70710678, 0, 1.0};
Point(9) = {7.29289322, 10.70710678, 0, 1.0};
Point(10) = {7.29289322, 9.29289322, 0, 1.0};
Point(11) = {8.70710678, 9.29289322, 0, 1.0};
//
Line(1) = {1, 2}; Transfinite Curve {1} = Nx1 Using Progression Rx1;
Line(2) = {2, 3}; Transfinite Curve {2} = Nx2 Using Progression Rx2;
Line(3) = {6, 5}; Transfinite Curve {3} = Nx1 Using Progression Rx1;
Line(4) = {5, 4}; Transfinite Curve {4} = Nx2 Using Progression Rx2;
Line(5) = {1, 6}; Transfinite Curve {5} = Ny Using Bump Ry;
Line(6) = {2, 5}; Transfinite Curve {6} = Ny Using Bump Ry;
Line(7) = {3, 4}; Transfinite Curve {7} = Ny Using Bump Ry;
// Cylinder curves
Circle(8) = {10, 7, 11}; Transfinite Curve {8} = Nc Using Progression Rc;
Circle(9) = {11, 7, 8}; Transfinite Curve {9} = Nc Using Progression Rc;
Circle(10) = {8, 7, 9}; Transfinite Curve {10} = Nc Using Progression Rc;
Circle(11) = {9, 7, 10}; Transfinite Curve {11} = Nc Using Progression Rc;
// Block lines
Line(12) = {1, 10}; Transfinite Curve {12} = Nb Using Progression Rb;
Line(13) = {2, 11}; Transfinite Curve {13} = Nb Using Progression Rb;
Line(14) = {5, 8}; Transfinite Curve {14} = Nb Using Progression Rb;
Line(15) = {6, 9}; Transfinite Curve {15} = Nb Using Progression Rb;

// Surfaces
Curve Loop(1) = {12, 8, -13, -1};
Plane Surface(1) = {1};
Curve Loop(2) = {13, 9, -14, -6};
Plane Surface(2) = {2};
Curve Loop(3) = {14, 10, -15, 3};
Plane Surface(3) = {3};
Curve Loop(4) = {15, 11, -12, 5};
Plane Surface(4) = {4};
Curve Loop(5) = {6, 4, -7, -2};
Plane Surface(5) = {5};
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Transfinite Surface {5};
Recombine Surface {1};
Recombine Surface {2};
Recombine Surface {3};
Recombine Surface {4};
Recombine Surface {5};

Extrude {0, 0, 1} {
  Surface{1}; Surface{2}; Surface{3}; Surface{4}; Surface{5}; 
  Layers{1};
  Recombine;
}
//+
Physical Surface("inlet", 126) = {102};
//+
Physical Surface("outlet", 127) = {120};
//+
Physical Surface("topAndBottom", 128) = {80, 116, 36, 124};
//+
Physical Surface("cylinder", 129) = {72, 94, 28, 50};
//+
Physical Surface("frontAndBack", 130) = {125, 59, 37, 103, 81, 5, 2, 3, 4, 1};
//+
Physical Volume("volume", 131) = {5, 1, 2, 3, 4};
