// Hose attachment settings
hose_inner_diameter = 32.5;
hose_outer_diameter = 37;
hose_lip_diameter = 40;
hose_insert_length = 5;
hose_lip_length = 10;
hose_taper_length = 3;
overlap = 0.5;

nozzle_join_length = 1;
nozzle_inner_diameter = 10;
nozzle_outer_diameter = 12;
nozzle_length = 80;

diameter_resolution = 10;

module dyson_attachment() {
  difference() {
    union() {
      translate([0,0,hose_insert_length]) hull() {
        translate([0,0,hose_taper_length]) cylinder(r= hose_lip_diameter/2, h=hose_lip_length);
        cylinder(r= hose_outer_diameter/2, h=hose_taper_length+overlap);
      }
      cylinder(r= hose_outer_diameter/2, h=hose_insert_length+overlap);
    }
    translate([0,0,-overlap]) cylinder(r=hose_inner_diameter/2, h=hose_insert_length+hose_lip_length+hose_taper_length+3*overlap);
  }
}

translate([0,0,hose_insert_length+hose_lip_length+hose_taper_length]) difference() {
  hull() {
    cylinder(r=nozzle_outer_diameter/2, h=nozzle_length);
    cylinder(r=hose_lip_diameter/2, h=nozzle_join_length);
  }
  translate([0,0,-overlap]) hull() {
    translate([0,0,2*overlap]) cylinder(r=nozzle_inner_diameter/2, h=nozzle_length+overlap);
    cylinder(r=hose_inner_diameter/2, h=nozzle_join_length+overlap);
  }
}
dyson_attachment();





