Nx = 80; Rx = 0.5; L = 10; H = 2;

//+
Point(1) = {0, 0, 0, 1.0};
Point(2) = {L, 0, 0, 1.0};
Point(3) = {L, H, 0, 1.0};
Point(4) = {0, H, 0, 1.0};
//+
Line(1) = {1, 2}; Transfinite Curve {1} = 2*Nx;
Line(2) = {2, 3}; Transfinite Curve {2} = Nx Using Bump Rx;
Line(3) = {3, 4}; Transfinite Curve {3} = 2*Nx;
Line(4) = {4, 1}; Transfinite Curve {4} = Nx Using Bump Rx;
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
//+
Physical Surface("frontAndBack", 27) = {26, 1};
//+
Physical Surface("topAndBottom", 28) = {21, 13};
//+
Physical Surface("inlet", 29) = {25};
//+
Physical Surface("outlet", 30) = {17};
//+
Physical Volume("volume", 31) = {1};
