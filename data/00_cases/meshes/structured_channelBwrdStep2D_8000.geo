NxLeft = 16; RxLeft = 1.00;
NxRight = 192; RxRight = 1.01;
NyCenter = 12; RyCenter = 0.20;
NySides = 16; RySides = 1.00;

//+
Point(1) = {-1, -0.5, 0, 1.0};
Point(2) = {0, -0.5, 0, 1.0};
Point(3) = {0, -1, 0, 1.0};
Point(4) = {32, -1, 0, 1.0};
Point(5) = {32, -0.5, 0, 1.0};
Point(6) = {32, 0.5, 0, 1.0};
Point(7) = {32, 1, 0, 1.0};
Point(8) = {0, 1, 0, 1.0};
Point(9) = {0, 0.5, 0, 1.0};
Point(10) = {-1, 0.5, 0, 1.0};
//+ Left square
Line(1) = {1, 2}; Transfinite Curve {1} = NxLeft Using Progression RxLeft;
Line(2) = {2, 9}; Transfinite Curve {2} = NyCenter Using Bump RyCenter;
Line(3) = {9, 10}; Transfinite Curve {3} = NxLeft Using Progression RxLeft;
Line(4) = {10, 1}; Transfinite Curve {4} = NyCenter Using Bump RyCenter;
//+ Right rectangle
Line(5) = {2, 3}; Transfinite Curve {5} = NySides Using Progression 1/RySides;
Line(6) = {3, 4}; Transfinite Curve {6} = NxRight Using Progression RxRight;
Line(7) = {4, 5}; Transfinite Curve {7} = NySides Using Progression RySides;
Line(8) = {5, 6}; Transfinite Curve {8} = NyCenter Using Bump RyCenter;
Line(9) = {6, 7}; Transfinite Curve {9} = NySides Using Progression 1/RySides;
Line(10) = {7, 8}; Transfinite Curve {10} = NxRight Using Progression 1/RxRight;
Line(11) = {8, 9}; Transfinite Curve {11} = NySides Using Progression RySides;
//+ Aux horizontal lines
Line(12) = {2, 5}; Transfinite Curve {12} = NxRight Using Progression RxRight;
Line(13) = {9, 6}; Transfinite Curve {13} = NxRight Using Progression RxRight;
//+
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};
Curve Loop(2) = {5, 6, 7, -12};
Plane Surface(2) = {2};
Curve Loop(3) = {12, 8, -13, -2};
Plane Surface(3) = {3};
Curve Loop(4) = {13, 9, 10, 11};
Plane Surface(4) = {4};
Transfinite Surface {1};
Transfinite Surface {2};
Transfinite Surface {3};
Transfinite Surface {4};
Recombine Surface {1};
Recombine Surface {2};
Recombine Surface {3};
Recombine Surface {4};
//+
Extrude {0, 0, 0.1} {
  Surface{1}; Surface{2}; Surface{3}; Surface{4};
  Layers{1};
  Recombine;
}
//+
Physical Surface("inlet", 102) = {34};
//+
Physical Surface("outlet", 103) = {70, 92, 52};
//+
Physical Surface("topAndBottom", 104) = {30, 22, 48, 96, 100, 44};
//+
Physical Surface("frontAndBack", 105) = {1, 35, 4, 101, 3, 79, 2, 57};
//+
Physical Volume("volume", 106) = {4, 3, 2, 1};
