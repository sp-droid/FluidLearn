Nx = 100; Rx = 4;

//+
Point(1) = {0, 0, 0, 1.0};
Point(2) = {1, 0, 0, 1.0};
Point(3) = {1, 1, 0, 1.0};
Point(4) = {0, 1, 0, 1.0};
//+
Line(1) = {1, 2}; Transfinite Curve {1} = Nx Using Bump Rx;;
Line(2) = {2, 3}; Transfinite Curve {2} = Nx Using Bump Rx;;
Line(3) = {3, 4}; Transfinite Curve {3} = Nx Using Bump Rx;;
Line(4) = {4, 1}; Transfinite Curve {4} = Nx Using Bump Rx;;
//+
Curve Loop(1) = {1, 2, 3, 4};
Plane Surface(1) = {1};
Transfinite Surface {1};
Recombine Surface {1};
//+
Extrude {0, 0, 0.1} {
  Surface{1};
  Layers{1};
  Recombine;
}//+
Physical Surface("top", 27) = {21};
//+
Physical Surface("frontAndBack", 28) = {26, 1};
//+
Physical Surface("down", 29) = {13};
Physical Surface("left", 30) = {25};
Physical Surface("right", 31) = {17};
//+
Physical Volume("volume", 32) = {1};
