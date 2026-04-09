// Params
Cxy = 5; Lx = 5*Cxy;
R = 0.5; Rxy = R/Sqrt(2);
Router = 6*R; Routerxy = Router/Sqrt(2);
//
Ninner = 45; Rinner = 0.96;
Nytopbottom = 20; Rytopbottom = 0.94;
Nymidleft = 20; Nymidright = 40;
Nxleft = 25; Nxmid = 25; Rxmid = 0.97; Nxright = 100; Rxright = 0.99;

// Boundary points
Point(1) = {0, 0, 0, 1.0};
Point(2) = {Lx, 0, 0, 1.0};
Point(3) = {Lx, 2*Cxy, 0, 1.0};
Point(4) = {0, 2*Cxy, 0, 1.0};
// Cylinder points
Point(7) = {Cxy, Cxy, 0, 1.0};
Point(8) = {Cxy-Rxy, Cxy+Rxy, 0, 1.0};
Point(9) = {Cxy+Rxy, Cxy+Rxy, 0, 1.0};
Point(10) = {Cxy+Rxy, Cxy-Rxy, 0, 1.0};
Point(11) = {Cxy-Rxy, Cxy-Rxy, 0, 1.0};
// Outer Cylinder points
Point(12) = {Cxy-Routerxy, Cxy+Routerxy, 0, 1.0};
Point(13) = {Cxy+Routerxy, Cxy+Routerxy, 0, 1.0};
Point(14) = {Cxy+Routerxy, Cxy-Routerxy, 0, 1.0};
Point(15) = {Cxy-Routerxy, Cxy-Routerxy, 0, 1.0};
// Inner cylinder lines
Line(1) = {12, 8}; Transfinite Curve {1} = Ninner Using Progression Rinner;
Line(2) = {13, 9}; Transfinite Curve {2} = Ninner Using Progression Rinner;
Line(3) = {14, 10}; Transfinite Curve {3} = Ninner Using Progression Rinner;
Line(4) = {15, 11}; Transfinite Curve {4} = Ninner Using Progression Rinner;
// Auxiliary points
Point(16) = {Cxy-Routerxy, 0, 0, 1.0};
Point(17) = {Cxy+Routerxy, 0, 0, 1.0};
Point(18) = {Lx, Cxy-Routerxy, 0, 1.0};
Point(19) = {Lx, Cxy+Routerxy, 0, 1.0};
Point(20) = {Cxy+Routerxy, 2*Cxy, 0, 1.0};
Point(21) = {Cxy-Routerxy, 2*Cxy, 0, 1.0};
Point(22) = {0, Cxy+Routerxy, 0, 1.0};
Point(23) = {0, Cxy-Routerxy, 0, 1.0};
// Cylinder curves
Circle(5) = {10, 7, 11}; Transfinite Curve {5} = Nxmid Using Progression 1/Rxmid;
Circle(6) = {11, 7, 8}; Transfinite Curve {6} = Nymidleft;
Circle(7) = {8, 7, 9}; Transfinite Curve {7} = Nxmid Using Progression Rxmid;
Circle(8) = {9, 7, 10}; Transfinite Curve {8} = Nymidright;
// Outer Cylinder curves
Circle(9) = {14, 7, 15}; Transfinite Curve {9} = Nxmid Using Progression 1/Rxmid;
Circle(10) = {15, 7, 12}; Transfinite Curve {10} = Nymidleft;
Circle(11) = {12, 7, 13}; Transfinite Curve {11} = Nxmid Using Progression Rxmid;
Circle(12) = {13, 7, 14}; Transfinite Curve {12} = Nymidright;
// Boundary lines
Line(13) = {1, 16}; Transfinite Curve {13} = Nxleft;
Line(14) = {16, 17}; Transfinite Curve {14} = Nxmid Using Progression Rxmid;
Line(15) = {17, 2}; Transfinite Curve {15} = Nxright Using Progression 1/Rxright;
Line(16) = {2, 18}; Transfinite Curve {16} = Nytopbottom Using Progression Rytopbottom;
Line(17) = {18, 19}; Transfinite Curve {17} = Nymidright;
Line(18) = {19, 3}; Transfinite Curve {18} = Nytopbottom Using Progression 1/Rytopbottom;
Line(19) = {3, 20}; Transfinite Curve {19} = Nxright Using Progression Rxright;
Line(20) = {20, 21}; Transfinite Curve {20} = Nxmid Using Progression 1/Rxmid;
Line(21) = {21, 4}; Transfinite Curve {21} = Nxleft;
Line(22) = {4, 22}; Transfinite Curve {22} = Nytopbottom Using Progression Rytopbottom;
Line(23) = {22, 23}; Transfinite Curve {23} = Nymidleft;
Line(24) = {23, 1}; Transfinite Curve {24} = Nytopbottom Using Progression 1/Rytopbottom;
// Auxiliary lines
Line(25) = {16, 15}; Transfinite Curve {25} = Nytopbottom Using Progression Rytopbottom;
Line(26) = {17, 14}; Transfinite Curve {26} = Nytopbottom Using Progression Rytopbottom;
Line(27) = {18, 14}; Transfinite Curve {27} = Nxright Using Progression Rxright;
Line(28) = {19, 13}; Transfinite Curve {28} = Nxright Using Progression Rxright;
Line(29) = {20, 13}; Transfinite Curve {29} = Nytopbottom Using Progression Rytopbottom;
Line(30) = {21, 12}; Transfinite Curve {30} = Nytopbottom Using Progression Rytopbottom;
Line(31) = {22, 12}; Transfinite Curve {31} = Nxleft;
Line(32) = {23, 15}; Transfinite Curve {32} = Nxleft;

//+
Curve Loop(1)  = {24, 13, 25, -32}; Plane Surface(1)  = {1};  Transfinite Surface {1};  Recombine Surface {1};
Curve Loop(2)  = {-25, 14, 26, 9};  Plane Surface(2)  = {2};  Transfinite Surface {2};  Recombine Surface {2};
Curve Loop(3)  = {-26, 15, 16, 27}; Plane Surface(3)  = {3};  Transfinite Surface {3};  Recombine Surface {3};
Curve Loop(4)  = {23, 32, 10, -31}; Plane Surface(4)  = {4};  Transfinite Surface {4};  Recombine Surface {4};
Curve Loop(5)  = {-10, 4, 6, -1};    Plane Surface(5)  = {5};  Transfinite Surface {5};  Recombine Surface {5};
Curve Loop(6)  = {-4, -9, 3, 5};     Plane Surface(6)  = {6};  Transfinite Surface {6};  Recombine Surface {6};
Curve Loop(7)  = {-3, -12, 2, 8};    Plane Surface(7)  = {7};  Transfinite Surface {7};  Recombine Surface {7};
Curve Loop(8)  = {12, -27, 17, 28}; Plane Surface(8)  = {8};  Transfinite Surface {8};  Recombine Surface {8};
Curve Loop(9)  = {7, -2, -11, 1};    Plane Surface(9)  = {9};  Transfinite Surface {9};  Recombine Surface {9};
Curve Loop(10) = {31, -30, 21, 22}; Plane Surface(10) = {10}; Transfinite Surface {10}; Recombine Surface {10};
Curve Loop(11) = {30, 11, -29, 20}; Plane Surface(11) = {11}; Transfinite Surface {11}; Recombine Surface {11};
Curve Loop(12) = {29, -28, 18, 19}; Plane Surface(12) = {12}; Transfinite Surface {12}; Recombine Surface {12};
//+
Extrude {0, 0, 1} {
  Surface{1}; Surface{2}; Surface{3}; Surface{4}; Surface{5}; Surface{6}; Surface{7}; Surface{8}; Surface{9}; Surface{10}; Surface{11}; Surface{12};
  Layers{1};
  Recombine;
}//+
Physical Surface("inlet", 297) = {251, 107, 41};
//+
Physical Surface("outlet", 298) = {291, 203, 93};
//+
Physical Surface("topAndBottom", 299) = {247, 273, 295, 89, 67, 45};
//+
Physical Surface("cylinder", 300) = {137, 163, 185, 217};
//+
Physical Surface("frontAndBack", 301) = {252, 10, 4, 120, 1, 54, 2, 76, 142, 5, 9, 230, 7, 186, 6, 164, 11, 274, 12, 296, 8, 208, 3, 98};
//+
Physical Volume("volume", 302) = {12, 11, 10, 4, 5, 9, 7, 6, 8, 3, 2, 1};
