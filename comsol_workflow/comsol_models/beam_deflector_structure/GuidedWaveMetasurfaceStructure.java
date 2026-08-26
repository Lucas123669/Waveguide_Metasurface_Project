/*
 * GuidedWaveMetasurfaceStructure.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 25 2026, 19:27 by COMSOL 6.3.0.290. */
public class GuidedWaveMetasurfaceStructure {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model
         .modelPath("D:\\xgxz333\\workspace\\graduate\\AI4COMSOL\\Code\\comsol-workflow-master\\guided-wave-metasurface-workflow\\comsol_models\\beam_deflector_structure");

    model.label("guided_wave_metasurface_structure");

    model.param().set("lambda0", "1.55[um]", "vacuum wavelength");
    model.param().set("freq0", "c_const/lambda0", "optical frequency");
    model.param().set("wg_w", "0.6[um]", "Si waveguide width");
    model.param().set("wg_h", "0.22[um]", "Si waveguide height");
    model.param().set("box_h", "3.0[um]", "buried oxide thickness");
    model.param().set("sub_h", "1.0[um]", "modeled Si handle thickness");
    model.param().set("Lambda", "0.575[um]", "three-atom supercell period");
    model.param().set("atom_pitch", "Lambda/3", "meta-atom center spacing");
    model.param().set("n_cells", "12", "number of modeled supercells");
    model.param().set("array_L", "n_cells*Lambda", "metasurface length");
    model.param().set("port_buffer", "2.0[um]", "bare waveguide at each end");
    model.param().set("device_L", "array_L+2*port_buffer", "total modeled length");
    model.param().set("domain_w", "4.0[um]", "transverse domain width");
    model.param().set("air_h", "3.0[um]", "air height above BOX");
    model.param().set("monitor_z", "1.0[um]", "monitor height above antenna");
    model.param().set("t_au", "0.03[um]", "each gold layer thickness");
    model.param().set("t_d", "0.03[um]", "antenna SiO2 spacer thickness");
    model.param().set("array_x0", "-array_L/2", "first supercell origin");
    model.param().set("sel_tol", "1[nm]", "boundary selection tolerance");
    model.param().set("n_air", "1.0");
    model.param().set("n_si", "3.48");
    model.param().set("n_sio2", "1.444");
    model.param().set("n_au", "0.55", "Au n seed at 1550 nm");
    model.param().set("k_au", "11.5", "Au extinction seed at 1550 nm");
    model.param().set("mesh_bulk", "lambda0/(10*n_si)", "paper minimum local wavelength step");
    model.param().set("mesh_metal", "0.015[um]", "local antenna mesh maximum");
    model.param().set("lx_p", "0.11[um]", "phase_plus_2pi_3_seed x size");
    model.param().set("ly_p", "0.19[um]", "phase_plus_2pi_3_seed y size");
    model.param().set("lx_z", "0.1[um]", "phase_zero_seed x size");
    model.param().set("ly_z", "0.275[um]", "phase_zero_seed y size");
    model.param().set("lx_m", "0.11[um]", "phase_minus_2pi_3_seed x size");
    model.param().set("ly_m", "0.295[um]", "phase_minus_2pi_3_seed y size");

    model.component().create("comp1", true);

    model.component("comp1").label("3D guided-wave-driven metasurface");

    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").label("SOI waveguide and Au-SiO2-Au meta-atoms");
    model.component("comp1").geom("geom1").lengthUnit("um");
    model.component("comp1").geom("geom1").create("air_domain", "Block");
    model.component("comp1").geom("geom1").feature("air_domain").label("air computational domain");
    model.component("comp1").geom("geom1").feature("air_domain").set("base", "corner");
    model.component("comp1").geom("geom1").feature("air_domain")
         .set("pos", new String[]{"-device_L/2", "-domain_w/2", "0"});
    model.component("comp1").geom("geom1").feature("air_domain")
         .set("size", new String[]{"device_L", "domain_w", "air_h"});
    model.component("comp1").geom("geom1").feature("air_domain").set("selresult", true);
    model.component("comp1").geom("geom1").create("box", "Block");
    model.component("comp1").geom("geom1").feature("box").label("3 um buried silicon dioxide");
    model.component("comp1").geom("geom1").feature("box").set("base", "corner");
    model.component("comp1").geom("geom1").feature("box")
         .set("pos", new String[]{"-device_L/2", "-domain_w/2", "-box_h"});
    model.component("comp1").geom("geom1").feature("box").set("size", new String[]{"device_L", "domain_w", "box_h"});
    model.component("comp1").geom("geom1").feature("box").set("selresult", true);
    model.component("comp1").geom("geom1").create("substrate", "Block");
    model.component("comp1").geom("geom1").feature("substrate").label("silicon handle (truncated)");
    model.component("comp1").geom("geom1").feature("substrate").set("base", "corner");
    model.component("comp1").geom("geom1").feature("substrate")
         .set("pos", new String[]{"-device_L/2", "-domain_w/2", "-box_h-sub_h"});
    model.component("comp1").geom("geom1").feature("substrate")
         .set("size", new String[]{"device_L", "domain_w", "sub_h"});
    model.component("comp1").geom("geom1").feature("substrate").set("selresult", true);
    model.component("comp1").geom("geom1").create("waveguide", "Block");
    model.component("comp1").geom("geom1").feature("waveguide").label("600 nm x 220 nm silicon ridge");
    model.component("comp1").geom("geom1").feature("waveguide").set("base", "corner");
    model.component("comp1").geom("geom1").feature("waveguide")
         .set("pos", new String[]{"-device_L/2", "-wg_w/2", "0"});
    model.component("comp1").geom("geom1").feature("waveguide")
         .set("size", new String[]{"device_L", "wg_w", "wg_h"});
    model.component("comp1").geom("geom1").feature("waveguide").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_000", "Block");
    model.component("comp1").geom("geom1").feature("au_b_000").label("atom 000 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_000").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_000")
         .set("pos", new String[]{"array_x0+(0+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_000").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_000").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_000", "Block");
    model.component("comp1").geom("geom1").feature("sp_000").label("atom 000 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_000").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_000")
         .set("pos", new String[]{"array_x0+(0+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_000").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_000").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_000", "Block");
    model.component("comp1").geom("geom1").feature("au_t_000").label("atom 000 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_000").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_000")
         .set("pos", new String[]{"array_x0+(0+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_000").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_000").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_001", "Block");
    model.component("comp1").geom("geom1").feature("au_b_001").label("atom 001 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_001").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_001")
         .set("pos", new String[]{"array_x0+(1+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_001").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_001").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_001", "Block");
    model.component("comp1").geom("geom1").feature("sp_001").label("atom 001 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_001").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_001")
         .set("pos", new String[]{"array_x0+(1+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_001").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_001").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_001", "Block");
    model.component("comp1").geom("geom1").feature("au_t_001").label("atom 001 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_001").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_001")
         .set("pos", new String[]{"array_x0+(1+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_001").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_001").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_002", "Block");
    model.component("comp1").geom("geom1").feature("au_b_002").label("atom 002 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_002").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_002")
         .set("pos", new String[]{"array_x0+(2+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_002").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_002").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_002", "Block");
    model.component("comp1").geom("geom1").feature("sp_002").label("atom 002 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_002").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_002")
         .set("pos", new String[]{"array_x0+(2+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_002").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_002").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_002", "Block");
    model.component("comp1").geom("geom1").feature("au_t_002").label("atom 002 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_002").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_002")
         .set("pos", new String[]{"array_x0+(2+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_002").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_002").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_003", "Block");
    model.component("comp1").geom("geom1").feature("au_b_003").label("atom 003 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_003").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_003")
         .set("pos", new String[]{"array_x0+(3+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_003").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_003").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_003", "Block");
    model.component("comp1").geom("geom1").feature("sp_003").label("atom 003 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_003").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_003")
         .set("pos", new String[]{"array_x0+(3+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_003").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_003").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_003", "Block");
    model.component("comp1").geom("geom1").feature("au_t_003").label("atom 003 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_003").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_003")
         .set("pos", new String[]{"array_x0+(3+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_003").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_003").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_004", "Block");
    model.component("comp1").geom("geom1").feature("au_b_004").label("atom 004 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_004").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_004")
         .set("pos", new String[]{"array_x0+(4+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_004").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_004").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_004", "Block");
    model.component("comp1").geom("geom1").feature("sp_004").label("atom 004 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_004").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_004")
         .set("pos", new String[]{"array_x0+(4+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_004").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_004").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_004", "Block");
    model.component("comp1").geom("geom1").feature("au_t_004").label("atom 004 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_004").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_004")
         .set("pos", new String[]{"array_x0+(4+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_004").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_004").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_005", "Block");
    model.component("comp1").geom("geom1").feature("au_b_005").label("atom 005 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_005").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_005")
         .set("pos", new String[]{"array_x0+(5+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_005").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_005").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_005", "Block");
    model.component("comp1").geom("geom1").feature("sp_005").label("atom 005 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_005").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_005")
         .set("pos", new String[]{"array_x0+(5+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_005").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_005").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_005", "Block");
    model.component("comp1").geom("geom1").feature("au_t_005").label("atom 005 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_005").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_005")
         .set("pos", new String[]{"array_x0+(5+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_005").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_005").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_006", "Block");
    model.component("comp1").geom("geom1").feature("au_b_006").label("atom 006 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_006").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_006")
         .set("pos", new String[]{"array_x0+(6+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_006").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_006").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_006", "Block");
    model.component("comp1").geom("geom1").feature("sp_006").label("atom 006 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_006").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_006")
         .set("pos", new String[]{"array_x0+(6+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_006").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_006").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_006", "Block");
    model.component("comp1").geom("geom1").feature("au_t_006").label("atom 006 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_006").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_006")
         .set("pos", new String[]{"array_x0+(6+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_006").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_006").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_007", "Block");
    model.component("comp1").geom("geom1").feature("au_b_007").label("atom 007 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_007").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_007")
         .set("pos", new String[]{"array_x0+(7+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_007").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_007").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_007", "Block");
    model.component("comp1").geom("geom1").feature("sp_007").label("atom 007 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_007").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_007")
         .set("pos", new String[]{"array_x0+(7+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_007").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_007").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_007", "Block");
    model.component("comp1").geom("geom1").feature("au_t_007").label("atom 007 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_007").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_007")
         .set("pos", new String[]{"array_x0+(7+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_007").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_007").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_008", "Block");
    model.component("comp1").geom("geom1").feature("au_b_008").label("atom 008 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_008").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_008")
         .set("pos", new String[]{"array_x0+(8+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_008").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_008").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_008", "Block");
    model.component("comp1").geom("geom1").feature("sp_008").label("atom 008 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_008").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_008")
         .set("pos", new String[]{"array_x0+(8+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_008").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_008").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_008", "Block");
    model.component("comp1").geom("geom1").feature("au_t_008").label("atom 008 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_008").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_008")
         .set("pos", new String[]{"array_x0+(8+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_008").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_008").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_009", "Block");
    model.component("comp1").geom("geom1").feature("au_b_009").label("atom 009 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_009").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_009")
         .set("pos", new String[]{"array_x0+(9+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_009").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_009").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_009", "Block");
    model.component("comp1").geom("geom1").feature("sp_009").label("atom 009 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_009").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_009")
         .set("pos", new String[]{"array_x0+(9+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_009").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_009").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_009", "Block");
    model.component("comp1").geom("geom1").feature("au_t_009").label("atom 009 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_009").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_009")
         .set("pos", new String[]{"array_x0+(9+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_009").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_009").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_010", "Block");
    model.component("comp1").geom("geom1").feature("au_b_010").label("atom 010 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_010").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_010")
         .set("pos", new String[]{"array_x0+(10+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_010").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_010").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_010", "Block");
    model.component("comp1").geom("geom1").feature("sp_010").label("atom 010 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_010").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_010")
         .set("pos", new String[]{"array_x0+(10+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_010").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_010").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_010", "Block");
    model.component("comp1").geom("geom1").feature("au_t_010").label("atom 010 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_010").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_010")
         .set("pos", new String[]{"array_x0+(10+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_010").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_010").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_011", "Block");
    model.component("comp1").geom("geom1").feature("au_b_011").label("atom 011 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_011").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_011")
         .set("pos", new String[]{"array_x0+(11+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_011").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_011").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_011", "Block");
    model.component("comp1").geom("geom1").feature("sp_011").label("atom 011 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_011").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_011")
         .set("pos", new String[]{"array_x0+(11+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_011").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_011").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_011", "Block");
    model.component("comp1").geom("geom1").feature("au_t_011").label("atom 011 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_011").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_011")
         .set("pos", new String[]{"array_x0+(11+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_011").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_011").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_012", "Block");
    model.component("comp1").geom("geom1").feature("au_b_012").label("atom 012 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_012").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_012")
         .set("pos", new String[]{"array_x0+(12+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_012").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_012").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_012", "Block");
    model.component("comp1").geom("geom1").feature("sp_012").label("atom 012 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_012").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_012")
         .set("pos", new String[]{"array_x0+(12+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_012").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_012").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_012", "Block");
    model.component("comp1").geom("geom1").feature("au_t_012").label("atom 012 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_012").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_012")
         .set("pos", new String[]{"array_x0+(12+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_012").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_012").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_013", "Block");
    model.component("comp1").geom("geom1").feature("au_b_013").label("atom 013 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_013").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_013")
         .set("pos", new String[]{"array_x0+(13+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_013").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_013").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_013", "Block");
    model.component("comp1").geom("geom1").feature("sp_013").label("atom 013 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_013").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_013")
         .set("pos", new String[]{"array_x0+(13+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_013").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_013").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_013", "Block");
    model.component("comp1").geom("geom1").feature("au_t_013").label("atom 013 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_013").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_013")
         .set("pos", new String[]{"array_x0+(13+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_013").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_013").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_014", "Block");
    model.component("comp1").geom("geom1").feature("au_b_014").label("atom 014 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_014").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_014")
         .set("pos", new String[]{"array_x0+(14+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_014").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_014").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_014", "Block");
    model.component("comp1").geom("geom1").feature("sp_014").label("atom 014 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_014").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_014")
         .set("pos", new String[]{"array_x0+(14+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_014").set("size", new String[]{"lx_m", "ly_m", "t_d"});

    return model;
  }

  public static Model run2(Model model) {
    model.component("comp1").geom("geom1").feature("sp_014").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_014", "Block");
    model.component("comp1").geom("geom1").feature("au_t_014").label("atom 014 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_014").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_014")
         .set("pos", new String[]{"array_x0+(14+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_014").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_014").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_015", "Block");
    model.component("comp1").geom("geom1").feature("au_b_015").label("atom 015 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_015").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_015")
         .set("pos", new String[]{"array_x0+(15+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_015").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_015").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_015", "Block");
    model.component("comp1").geom("geom1").feature("sp_015").label("atom 015 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_015").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_015")
         .set("pos", new String[]{"array_x0+(15+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_015").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_015").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_015", "Block");
    model.component("comp1").geom("geom1").feature("au_t_015").label("atom 015 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_015").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_015")
         .set("pos", new String[]{"array_x0+(15+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_015").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_015").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_016", "Block");
    model.component("comp1").geom("geom1").feature("au_b_016").label("atom 016 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_016").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_016")
         .set("pos", new String[]{"array_x0+(16+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_016").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_016").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_016", "Block");
    model.component("comp1").geom("geom1").feature("sp_016").label("atom 016 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_016").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_016")
         .set("pos", new String[]{"array_x0+(16+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_016").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_016").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_016", "Block");
    model.component("comp1").geom("geom1").feature("au_t_016").label("atom 016 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_016").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_016")
         .set("pos", new String[]{"array_x0+(16+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_016").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_016").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_017", "Block");
    model.component("comp1").geom("geom1").feature("au_b_017").label("atom 017 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_017").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_017")
         .set("pos", new String[]{"array_x0+(17+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_017").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_017").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_017", "Block");
    model.component("comp1").geom("geom1").feature("sp_017").label("atom 017 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_017").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_017")
         .set("pos", new String[]{"array_x0+(17+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_017").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_017").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_017", "Block");
    model.component("comp1").geom("geom1").feature("au_t_017").label("atom 017 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_017").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_017")
         .set("pos", new String[]{"array_x0+(17+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_017").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_017").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_018", "Block");
    model.component("comp1").geom("geom1").feature("au_b_018").label("atom 018 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_018").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_018")
         .set("pos", new String[]{"array_x0+(18+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_018").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_018").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_018", "Block");
    model.component("comp1").geom("geom1").feature("sp_018").label("atom 018 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_018").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_018")
         .set("pos", new String[]{"array_x0+(18+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_018").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_018").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_018", "Block");
    model.component("comp1").geom("geom1").feature("au_t_018").label("atom 018 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_018").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_018")
         .set("pos", new String[]{"array_x0+(18+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_018").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_018").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_019", "Block");
    model.component("comp1").geom("geom1").feature("au_b_019").label("atom 019 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_019").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_019")
         .set("pos", new String[]{"array_x0+(19+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_019").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_019").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_019", "Block");
    model.component("comp1").geom("geom1").feature("sp_019").label("atom 019 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_019").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_019")
         .set("pos", new String[]{"array_x0+(19+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_019").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_019").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_019", "Block");
    model.component("comp1").geom("geom1").feature("au_t_019").label("atom 019 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_019").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_019")
         .set("pos", new String[]{"array_x0+(19+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_019").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_019").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_020", "Block");
    model.component("comp1").geom("geom1").feature("au_b_020").label("atom 020 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_020").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_020")
         .set("pos", new String[]{"array_x0+(20+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_020").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_020").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_020", "Block");
    model.component("comp1").geom("geom1").feature("sp_020").label("atom 020 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_020").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_020")
         .set("pos", new String[]{"array_x0+(20+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_020").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_020").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_020", "Block");
    model.component("comp1").geom("geom1").feature("au_t_020").label("atom 020 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_020").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_020")
         .set("pos", new String[]{"array_x0+(20+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_020").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_020").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_021", "Block");
    model.component("comp1").geom("geom1").feature("au_b_021").label("atom 021 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_021").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_021")
         .set("pos", new String[]{"array_x0+(21+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_021").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_021").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_021", "Block");
    model.component("comp1").geom("geom1").feature("sp_021").label("atom 021 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_021").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_021")
         .set("pos", new String[]{"array_x0+(21+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_021").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_021").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_021", "Block");
    model.component("comp1").geom("geom1").feature("au_t_021").label("atom 021 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_021").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_021")
         .set("pos", new String[]{"array_x0+(21+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_021").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_021").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_022", "Block");
    model.component("comp1").geom("geom1").feature("au_b_022").label("atom 022 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_022").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_022")
         .set("pos", new String[]{"array_x0+(22+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_022").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_022").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_022", "Block");
    model.component("comp1").geom("geom1").feature("sp_022").label("atom 022 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_022").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_022")
         .set("pos", new String[]{"array_x0+(22+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_022").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_022").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_022", "Block");
    model.component("comp1").geom("geom1").feature("au_t_022").label("atom 022 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_022").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_022")
         .set("pos", new String[]{"array_x0+(22+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_022").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_022").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_023", "Block");
    model.component("comp1").geom("geom1").feature("au_b_023").label("atom 023 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_023").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_023")
         .set("pos", new String[]{"array_x0+(23+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_023").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_023").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_023", "Block");
    model.component("comp1").geom("geom1").feature("sp_023").label("atom 023 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_023").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_023")
         .set("pos", new String[]{"array_x0+(23+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_023").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_023").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_023", "Block");
    model.component("comp1").geom("geom1").feature("au_t_023").label("atom 023 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_023").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_023")
         .set("pos", new String[]{"array_x0+(23+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_023").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_023").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_024", "Block");
    model.component("comp1").geom("geom1").feature("au_b_024").label("atom 024 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_024").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_024")
         .set("pos", new String[]{"array_x0+(24+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_024").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_024").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_024", "Block");
    model.component("comp1").geom("geom1").feature("sp_024").label("atom 024 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_024").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_024")
         .set("pos", new String[]{"array_x0+(24+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_024").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_024").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_024", "Block");
    model.component("comp1").geom("geom1").feature("au_t_024").label("atom 024 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_024").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_024")
         .set("pos", new String[]{"array_x0+(24+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_024").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_024").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_025", "Block");
    model.component("comp1").geom("geom1").feature("au_b_025").label("atom 025 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_025").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_025")
         .set("pos", new String[]{"array_x0+(25+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_025").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_025").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_025", "Block");
    model.component("comp1").geom("geom1").feature("sp_025").label("atom 025 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_025").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_025")
         .set("pos", new String[]{"array_x0+(25+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_025").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_025").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_025", "Block");
    model.component("comp1").geom("geom1").feature("au_t_025").label("atom 025 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_025").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_025")
         .set("pos", new String[]{"array_x0+(25+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_025").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_025").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_026", "Block");
    model.component("comp1").geom("geom1").feature("au_b_026").label("atom 026 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_026").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_026")
         .set("pos", new String[]{"array_x0+(26+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_026").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_026").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_026", "Block");
    model.component("comp1").geom("geom1").feature("sp_026").label("atom 026 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_026").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_026")
         .set("pos", new String[]{"array_x0+(26+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_026").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_026").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_026", "Block");
    model.component("comp1").geom("geom1").feature("au_t_026").label("atom 026 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_026").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_026")
         .set("pos", new String[]{"array_x0+(26+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_026").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_026").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_027", "Block");
    model.component("comp1").geom("geom1").feature("au_b_027").label("atom 027 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_027").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_027")
         .set("pos", new String[]{"array_x0+(27+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_027").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_027").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_027", "Block");
    model.component("comp1").geom("geom1").feature("sp_027").label("atom 027 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_027").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_027")
         .set("pos", new String[]{"array_x0+(27+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_027").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_027").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_027", "Block");
    model.component("comp1").geom("geom1").feature("au_t_027").label("atom 027 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_027").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_027")
         .set("pos", new String[]{"array_x0+(27+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_027").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_027").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_028", "Block");
    model.component("comp1").geom("geom1").feature("au_b_028").label("atom 028 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_028").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_028")
         .set("pos", new String[]{"array_x0+(28+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_028").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_028").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_028", "Block");
    model.component("comp1").geom("geom1").feature("sp_028").label("atom 028 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_028").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_028")
         .set("pos", new String[]{"array_x0+(28+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_028").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_028").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_028", "Block");
    model.component("comp1").geom("geom1").feature("au_t_028").label("atom 028 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_028").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_028")
         .set("pos", new String[]{"array_x0+(28+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_028").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_028").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_029", "Block");
    model.component("comp1").geom("geom1").feature("au_b_029").label("atom 029 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_029").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_029")
         .set("pos", new String[]{"array_x0+(29+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_029").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_029").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_029", "Block");
    model.component("comp1").geom("geom1").feature("sp_029").label("atom 029 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_029").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_029")
         .set("pos", new String[]{"array_x0+(29+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_029").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_029").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_029", "Block");
    model.component("comp1").geom("geom1").feature("au_t_029").label("atom 029 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_029").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_029")
         .set("pos", new String[]{"array_x0+(29+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_029").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_029").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_030", "Block");
    model.component("comp1").geom("geom1").feature("au_b_030").label("atom 030 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_030").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_030")
         .set("pos", new String[]{"array_x0+(30+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_030").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_030").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_030", "Block");
    model.component("comp1").geom("geom1").feature("sp_030").label("atom 030 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_030").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_030")
         .set("pos", new String[]{"array_x0+(30+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_030").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_030").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_030", "Block");
    model.component("comp1").geom("geom1").feature("au_t_030").label("atom 030 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_030").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_030")
         .set("pos", new String[]{"array_x0+(30+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_030").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_030").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_031", "Block");
    model.component("comp1").geom("geom1").feature("au_b_031").label("atom 031 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_031").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_031")
         .set("pos", new String[]{"array_x0+(31+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_031").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_031").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_031", "Block");
    model.component("comp1").geom("geom1").feature("sp_031").label("atom 031 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_031").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_031")
         .set("pos", new String[]{"array_x0+(31+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_031").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_031").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_031", "Block");
    model.component("comp1").geom("geom1").feature("au_t_031").label("atom 031 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_031").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_031")
         .set("pos", new String[]{"array_x0+(31+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_031").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_031").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_032", "Block");
    model.component("comp1").geom("geom1").feature("au_b_032").label("atom 032 bottom Au phase m");

    return model;
  }

  public static Model run3(Model model) {
    model.component("comp1").geom("geom1").feature("au_b_032").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_032")
         .set("pos", new String[]{"array_x0+(32+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_032").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_032").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_032", "Block");
    model.component("comp1").geom("geom1").feature("sp_032").label("atom 032 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_032").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_032")
         .set("pos", new String[]{"array_x0+(32+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_032").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_032").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_032", "Block");
    model.component("comp1").geom("geom1").feature("au_t_032").label("atom 032 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_032").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_032")
         .set("pos", new String[]{"array_x0+(32+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_032").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_032").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_033", "Block");
    model.component("comp1").geom("geom1").feature("au_b_033").label("atom 033 bottom Au phase p");
    model.component("comp1").geom("geom1").feature("au_b_033").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_033")
         .set("pos", new String[]{"array_x0+(33+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_033").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_033").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_033", "Block");
    model.component("comp1").geom("geom1").feature("sp_033").label("atom 033 SiO2 spacer phase p");
    model.component("comp1").geom("geom1").feature("sp_033").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_033")
         .set("pos", new String[]{"array_x0+(33+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_033").set("size", new String[]{"lx_p", "ly_p", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_033").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_033", "Block");
    model.component("comp1").geom("geom1").feature("au_t_033").label("atom 033 top Au phase p");
    model.component("comp1").geom("geom1").feature("au_t_033").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_033")
         .set("pos", new String[]{"array_x0+(33+0.5)*atom_pitch-lx_p/2", "-ly_p/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_033").set("size", new String[]{"lx_p", "ly_p", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_033").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_034", "Block");
    model.component("comp1").geom("geom1").feature("au_b_034").label("atom 034 bottom Au phase z");
    model.component("comp1").geom("geom1").feature("au_b_034").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_034")
         .set("pos", new String[]{"array_x0+(34+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_034").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_034").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_034", "Block");
    model.component("comp1").geom("geom1").feature("sp_034").label("atom 034 SiO2 spacer phase z");
    model.component("comp1").geom("geom1").feature("sp_034").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_034")
         .set("pos", new String[]{"array_x0+(34+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_034").set("size", new String[]{"lx_z", "ly_z", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_034").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_034", "Block");
    model.component("comp1").geom("geom1").feature("au_t_034").label("atom 034 top Au phase z");
    model.component("comp1").geom("geom1").feature("au_t_034").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_034")
         .set("pos", new String[]{"array_x0+(34+0.5)*atom_pitch-lx_z/2", "-ly_z/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_034").set("size", new String[]{"lx_z", "ly_z", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_034").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_b_035", "Block");
    model.component("comp1").geom("geom1").feature("au_b_035").label("atom 035 bottom Au phase m");
    model.component("comp1").geom("geom1").feature("au_b_035").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_b_035")
         .set("pos", new String[]{"array_x0+(35+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h"});
    model.component("comp1").geom("geom1").feature("au_b_035").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_b_035").set("selresult", true);
    model.component("comp1").geom("geom1").create("sp_035", "Block");
    model.component("comp1").geom("geom1").feature("sp_035").label("atom 035 SiO2 spacer phase m");
    model.component("comp1").geom("geom1").feature("sp_035").set("base", "corner");
    model.component("comp1").geom("geom1").feature("sp_035")
         .set("pos", new String[]{"array_x0+(35+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au"});
    model.component("comp1").geom("geom1").feature("sp_035").set("size", new String[]{"lx_m", "ly_m", "t_d"});
    model.component("comp1").geom("geom1").feature("sp_035").set("selresult", true);
    model.component("comp1").geom("geom1").create("au_t_035", "Block");
    model.component("comp1").geom("geom1").feature("au_t_035").label("atom 035 top Au phase m");
    model.component("comp1").geom("geom1").feature("au_t_035").set("base", "corner");
    model.component("comp1").geom("geom1").feature("au_t_035")
         .set("pos", new String[]{"array_x0+(35+0.5)*atom_pitch-lx_m/2", "-ly_m/2", "wg_h+t_au+t_d"});
    model.component("comp1").geom("geom1").feature("au_t_035").set("size", new String[]{"lx_m", "ly_m", "t_au"});
    model.component("comp1").geom("geom1").feature("au_t_035").set("selresult", true);
    model.component("comp1").geom("geom1").feature("fin").set("action", "union");
    model.component("comp1").geom("geom1").run();

    model.component("comp1").selection().create("sel_si", "Union");
    model.component("comp1").selection("sel_si").label("silicon waveguide and handle");
    model.component("comp1").selection("sel_si").geom("geom1", 3);
    model.component("comp1").selection("sel_si")
         .set("input", new String[]{"geom1_waveguide_dom", "geom1_substrate_dom"});
    model.component("comp1").selection().create("sel_au", "Union");
    model.component("comp1").selection("sel_au").label("all gold antenna layers");
    model.component("comp1").selection("sel_au").geom("geom1", 3);
    model.component("comp1").selection("sel_au")
         .set("input", new String[]{"geom1_au_b_000_dom", "geom1_au_b_001_dom", "geom1_au_b_002_dom", "geom1_au_b_003_dom", "geom1_au_b_004_dom", "geom1_au_b_005_dom", "geom1_au_b_006_dom", "geom1_au_b_007_dom", "geom1_au_b_008_dom", "geom1_au_b_009_dom", 
         "geom1_au_b_010_dom", "geom1_au_b_011_dom", "geom1_au_b_012_dom", "geom1_au_b_013_dom", "geom1_au_b_014_dom", "geom1_au_b_015_dom", "geom1_au_b_016_dom", "geom1_au_b_017_dom", "geom1_au_b_018_dom", "geom1_au_b_019_dom", 
         "geom1_au_b_020_dom", "geom1_au_b_021_dom", "geom1_au_b_022_dom", "geom1_au_b_023_dom", "geom1_au_b_024_dom", "geom1_au_b_025_dom", "geom1_au_b_026_dom", "geom1_au_b_027_dom", "geom1_au_b_028_dom", "geom1_au_b_029_dom", 
         "geom1_au_b_030_dom", "geom1_au_b_031_dom", "geom1_au_b_032_dom", "geom1_au_b_033_dom", "geom1_au_b_034_dom", "geom1_au_b_035_dom", "geom1_au_t_000_dom", "geom1_au_t_001_dom", "geom1_au_t_002_dom", "geom1_au_t_003_dom", 
         "geom1_au_t_004_dom", "geom1_au_t_005_dom", "geom1_au_t_006_dom", "geom1_au_t_007_dom", "geom1_au_t_008_dom", "geom1_au_t_009_dom", "geom1_au_t_010_dom", "geom1_au_t_011_dom", "geom1_au_t_012_dom", "geom1_au_t_013_dom", 
         "geom1_au_t_014_dom", "geom1_au_t_015_dom", "geom1_au_t_016_dom", "geom1_au_t_017_dom", "geom1_au_t_018_dom", "geom1_au_t_019_dom", "geom1_au_t_020_dom", "geom1_au_t_021_dom", "geom1_au_t_022_dom", "geom1_au_t_023_dom", 
         "geom1_au_t_024_dom", "geom1_au_t_025_dom", "geom1_au_t_026_dom", "geom1_au_t_027_dom", "geom1_au_t_028_dom", "geom1_au_t_029_dom", "geom1_au_t_030_dom", "geom1_au_t_031_dom", "geom1_au_t_032_dom", "geom1_au_t_033_dom", 
         "geom1_au_t_034_dom", "geom1_au_t_035_dom"});
    model.component("comp1").selection().create("sel_sio2", "Union");
    model.component("comp1").selection("sel_sio2").label("BOX and antenna SiO2");
    model.component("comp1").selection("sel_sio2").geom("geom1", 3);
    model.component("comp1").selection("sel_sio2")
         .set("input", new String[]{"geom1_box_dom", "geom1_sp_000_dom", "geom1_sp_001_dom", "geom1_sp_002_dom", "geom1_sp_003_dom", "geom1_sp_004_dom", "geom1_sp_005_dom", "geom1_sp_006_dom", "geom1_sp_007_dom", "geom1_sp_008_dom", 
         "geom1_sp_009_dom", "geom1_sp_010_dom", "geom1_sp_011_dom", "geom1_sp_012_dom", "geom1_sp_013_dom", "geom1_sp_014_dom", "geom1_sp_015_dom", "geom1_sp_016_dom", "geom1_sp_017_dom", "geom1_sp_018_dom", 
         "geom1_sp_019_dom", "geom1_sp_020_dom", "geom1_sp_021_dom", "geom1_sp_022_dom", "geom1_sp_023_dom", "geom1_sp_024_dom", "geom1_sp_025_dom", "geom1_sp_026_dom", "geom1_sp_027_dom", "geom1_sp_028_dom", 
         "geom1_sp_029_dom", "geom1_sp_030_dom", "geom1_sp_031_dom", "geom1_sp_032_dom", "geom1_sp_033_dom", "geom1_sp_034_dom", "geom1_sp_035_dom"});
    model.component("comp1").selection().create("sel_atoms", "Union");
    model.component("comp1").selection("sel_atoms").label("all antenna domains");
    model.component("comp1").selection("sel_atoms").geom("geom1", 3);
    model.component("comp1").selection("sel_atoms")
         .set("input", new String[]{"geom1_au_b_000_dom", "geom1_sp_000_dom", "geom1_au_t_000_dom", "geom1_au_b_001_dom", "geom1_sp_001_dom", "geom1_au_t_001_dom", "geom1_au_b_002_dom", "geom1_sp_002_dom", "geom1_au_t_002_dom", "geom1_au_b_003_dom", 
         "geom1_sp_003_dom", "geom1_au_t_003_dom", "geom1_au_b_004_dom", "geom1_sp_004_dom", "geom1_au_t_004_dom", "geom1_au_b_005_dom", "geom1_sp_005_dom", "geom1_au_t_005_dom", "geom1_au_b_006_dom", "geom1_sp_006_dom", 
         "geom1_au_t_006_dom", "geom1_au_b_007_dom", "geom1_sp_007_dom", "geom1_au_t_007_dom", "geom1_au_b_008_dom", "geom1_sp_008_dom", "geom1_au_t_008_dom", "geom1_au_b_009_dom", "geom1_sp_009_dom", "geom1_au_t_009_dom", 
         "geom1_au_b_010_dom", "geom1_sp_010_dom", "geom1_au_t_010_dom", "geom1_au_b_011_dom", "geom1_sp_011_dom", "geom1_au_t_011_dom", "geom1_au_b_012_dom", "geom1_sp_012_dom", "geom1_au_t_012_dom", "geom1_au_b_013_dom", 
         "geom1_sp_013_dom", "geom1_au_t_013_dom", "geom1_au_b_014_dom", "geom1_sp_014_dom", "geom1_au_t_014_dom", "geom1_au_b_015_dom", "geom1_sp_015_dom", "geom1_au_t_015_dom", "geom1_au_b_016_dom", "geom1_sp_016_dom", 
         "geom1_au_t_016_dom", "geom1_au_b_017_dom", "geom1_sp_017_dom", "geom1_au_t_017_dom", "geom1_au_b_018_dom", "geom1_sp_018_dom", "geom1_au_t_018_dom", "geom1_au_b_019_dom", "geom1_sp_019_dom", "geom1_au_t_019_dom", 
         "geom1_au_b_020_dom", "geom1_sp_020_dom", "geom1_au_t_020_dom", "geom1_au_b_021_dom", "geom1_sp_021_dom", "geom1_au_t_021_dom", "geom1_au_b_022_dom", "geom1_sp_022_dom", "geom1_au_t_022_dom", "geom1_au_b_023_dom", 
         "geom1_sp_023_dom", "geom1_au_t_023_dom", "geom1_au_b_024_dom", "geom1_sp_024_dom", "geom1_au_t_024_dom", "geom1_au_b_025_dom", "geom1_sp_025_dom", "geom1_au_t_025_dom", "geom1_au_b_026_dom", "geom1_sp_026_dom", 
         "geom1_au_t_026_dom", "geom1_au_b_027_dom", "geom1_sp_027_dom", "geom1_au_t_027_dom", "geom1_au_b_028_dom", "geom1_sp_028_dom", "geom1_au_t_028_dom", "geom1_au_b_029_dom", "geom1_sp_029_dom", "geom1_au_t_029_dom", 
         "geom1_au_b_030_dom", "geom1_sp_030_dom", "geom1_au_t_030_dom", "geom1_au_b_031_dom", "geom1_sp_031_dom", "geom1_au_t_031_dom", "geom1_au_b_032_dom", "geom1_sp_032_dom", "geom1_au_t_032_dom", "geom1_au_b_033_dom", 
         "geom1_sp_033_dom", "geom1_au_t_033_dom", "geom1_au_b_034_dom", "geom1_sp_034_dom", "geom1_au_t_034_dom", "geom1_au_b_035_dom", "geom1_sp_035_dom", "geom1_au_t_035_dom"});
    model.component("comp1").selection().create("sel_non_air", "Union");
    model.component("comp1").selection("sel_non_air").label("all non-air domains");
    model.component("comp1").selection("sel_non_air").geom("geom1", 3);
    model.component("comp1").selection("sel_non_air").set("input", new String[]{"sel_si", "sel_au", "sel_sio2"});
    model.component("comp1").selection().create("sel_air", "Difference");
    model.component("comp1").selection("sel_air").label("air only");
    model.component("comp1").selection("sel_air").geom("geom1", 3);
    model.component("comp1").selection("sel_air").set("add", new String[]{"geom1_air_domain_dom"});
    model.component("comp1").selection("sel_air").set("subtract", new String[]{"sel_non_air"});
    model.component("comp1").selection().create("sel_port_in", "Box");
    model.component("comp1").selection("sel_port_in").label("input port x-min");
    model.component("comp1").selection("sel_port_in").geom("geom1", 2);
    model.component("comp1").selection("sel_port_in").set("condition", "inside");
    model.component("comp1").selection("sel_port_in").set("xmin", "-device_L/2-sel_tol");
    model.component("comp1").selection("sel_port_in").set("xmax", "-device_L/2+sel_tol");
    model.component("comp1").selection("sel_port_in").set("ymin", "-domain_w/2-sel_tol");
    model.component("comp1").selection("sel_port_in").set("ymax", "domain_w/2+sel_tol");
    model.component("comp1").selection("sel_port_in").set("zmin", "-box_h-sub_h-sel_tol");
    model.component("comp1").selection("sel_port_in").set("zmax", "air_h+sel_tol");
    model.component("comp1").selection().create("sel_port_out", "Box");
    model.component("comp1").selection("sel_port_out").label("output port x-max");
    model.component("comp1").selection("sel_port_out").geom("geom1", 2);
    model.component("comp1").selection("sel_port_out").set("condition", "inside");
    model.component("comp1").selection("sel_port_out").set("xmin", "device_L/2-sel_tol");
    model.component("comp1").selection("sel_port_out").set("xmax", "device_L/2+sel_tol");
    model.component("comp1").selection("sel_port_out").set("ymin", "-domain_w/2-sel_tol");
    model.component("comp1").selection("sel_port_out").set("ymax", "domain_w/2+sel_tol");
    model.component("comp1").selection("sel_port_out").set("zmin", "-box_h-sub_h-sel_tol");
    model.component("comp1").selection("sel_port_out").set("zmax", "air_h+sel_tol");
    model.component("comp1").selection().create("sel_open_top", "Box");
    model.component("comp1").selection("sel_open_top").label("top scattering boundary");
    model.component("comp1").selection("sel_open_top").geom("geom1", 2);
    model.component("comp1").selection("sel_open_top").set("condition", "inside");
    model.component("comp1").selection("sel_open_top").set("xmin", "-device_L/2-sel_tol");
    model.component("comp1").selection("sel_open_top").set("xmax", "device_L/2+sel_tol");
    model.component("comp1").selection("sel_open_top").set("ymin", "-domain_w/2-sel_tol");
    model.component("comp1").selection("sel_open_top").set("ymax", "domain_w/2+sel_tol");
    model.component("comp1").selection("sel_open_top").set("zmin", "air_h-sel_tol");
    model.component("comp1").selection("sel_open_top").set("zmax", "air_h+sel_tol");
    model.component("comp1").selection().create("sel_open_bottom", "Box");
    model.component("comp1").selection("sel_open_bottom").label("bottom scattering boundary");
    model.component("comp1").selection("sel_open_bottom").geom("geom1", 2);
    model.component("comp1").selection("sel_open_bottom").set("condition", "inside");
    model.component("comp1").selection("sel_open_bottom").set("xmin", "-device_L/2-sel_tol");
    model.component("comp1").selection("sel_open_bottom").set("xmax", "device_L/2+sel_tol");
    model.component("comp1").selection("sel_open_bottom").set("ymin", "-domain_w/2-sel_tol");
    model.component("comp1").selection("sel_open_bottom").set("ymax", "domain_w/2+sel_tol");
    model.component("comp1").selection("sel_open_bottom").set("zmin", "-box_h-sub_h-sel_tol");
    model.component("comp1").selection("sel_open_bottom").set("zmax", "-box_h-sub_h+sel_tol");
    model.component("comp1").selection().create("sel_open_ymin", "Box");
    model.component("comp1").selection("sel_open_ymin").label("negative-y scattering boundary");
    model.component("comp1").selection("sel_open_ymin").geom("geom1", 2);
    model.component("comp1").selection("sel_open_ymin").set("condition", "inside");
    model.component("comp1").selection("sel_open_ymin").set("xmin", "-device_L/2-sel_tol");
    model.component("comp1").selection("sel_open_ymin").set("xmax", "device_L/2+sel_tol");
    model.component("comp1").selection("sel_open_ymin").set("ymin", "-domain_w/2-sel_tol");
    model.component("comp1").selection("sel_open_ymin").set("ymax", "-domain_w/2+sel_tol");
    model.component("comp1").selection("sel_open_ymin").set("zmin", "-box_h-sub_h-sel_tol");
    model.component("comp1").selection("sel_open_ymin").set("zmax", "air_h+sel_tol");
    model.component("comp1").selection().create("sel_open_ymax", "Box");
    model.component("comp1").selection("sel_open_ymax").label("positive-y scattering boundary");
    model.component("comp1").selection("sel_open_ymax").geom("geom1", 2);
    model.component("comp1").selection("sel_open_ymax").set("condition", "inside");
    model.component("comp1").selection("sel_open_ymax").set("xmin", "-device_L/2-sel_tol");
    model.component("comp1").selection("sel_open_ymax").set("xmax", "device_L/2+sel_tol");
    model.component("comp1").selection("sel_open_ymax").set("ymin", "domain_w/2-sel_tol");
    model.component("comp1").selection("sel_open_ymax").set("ymax", "domain_w/2+sel_tol");
    model.component("comp1").selection("sel_open_ymax").set("zmin", "-box_h-sub_h-sel_tol");
    model.component("comp1").selection("sel_open_ymax").set("zmax", "air_h+sel_tol");
    model.component("comp1").selection().create("sel_open", "Union");
    model.component("comp1").selection("sel_open").label("all non-port exterior boundaries");
    model.component("comp1").selection("sel_open").geom("geom1", 2);
    model.component("comp1").selection("sel_open")
         .set("input", new String[]{"sel_open_top", "sel_open_bottom", "sel_open_ymin", "sel_open_ymax"});

    model.component("comp1").material().create("mat_air", "Common");
    model.component("comp1").material("mat_air").label("Air");
    model.component("comp1").material("mat_air").selection().named("sel_air");
    model.component("comp1").material("mat_air").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_air").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_air", "0", "0", "0", "n_air", "0", "0", "0", "n_air"});
    model.component("comp1").material("mat_air").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});
    model.component("comp1").material().create("mat_si", "Common");
    model.component("comp1").material("mat_si").label("Silicon");
    model.component("comp1").material("mat_si").selection().named("sel_si");
    model.component("comp1").material("mat_si").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_si").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_si", "0", "0", "0", "n_si", "0", "0", "0", "n_si"});
    model.component("comp1").material("mat_si").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});
    model.component("comp1").material().create("mat_sio2", "Common");
    model.component("comp1").material("mat_sio2").label("Silicon dioxide");
    model.component("comp1").material("mat_sio2").selection().named("sel_sio2");
    model.component("comp1").material("mat_sio2").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_sio2").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_sio2", "0", "0", "0", "n_sio2", "0", "0", "0", "n_sio2"});
    model.component("comp1").material("mat_sio2").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});
    model.component("comp1").material().create("mat_au", "Common");
    model.component("comp1").material("mat_au").label("Gold seed optical constants");
    model.component("comp1").material("mat_au").selection().named("sel_au");
    model.component("comp1").material("mat_au").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_au").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_au", "0", "0", "0", "n_au", "0", "0", "0", "n_au"});
    model.component("comp1").material("mat_au").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"k_au", "0", "0", "0", "k_au", "0", "0", "0", "k_au"});

    model.component("comp1").physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1");
    model.component("comp1").physics("ewfd").label("Electromagnetic Waves, Frequency Domain");
    model.component("comp1").physics("ewfd").create("port1", "Port", 2);
    model.component("comp1").physics("ewfd").feature("port1").label("TE00 numeric input port");
    model.component("comp1").physics("ewfd").feature("port1").selection().named("sel_port_in");
    model.component("comp1").physics("ewfd").feature("port1").set("PortType", "Numeric");
    model.component("comp1").physics("ewfd").feature("port1").set("PortExcitation", "on");
    model.component("comp1").physics("ewfd").create("port2", "Port", 2);
    model.component("comp1").physics("ewfd").feature("port2").label("numeric output port");
    model.component("comp1").physics("ewfd").feature("port2").selection().named("sel_port_out");
    model.component("comp1").physics("ewfd").feature("port2").set("PortType", "Numeric");
    model.component("comp1").physics("ewfd").feature("port2").set("PortExcitation", "off");
    model.component("comp1").physics("ewfd").create("sctr1", "Scattering", 2);
    model.component("comp1").physics("ewfd").feature("sctr1")
         .label("top, bottom, and transverse scattering boundaries");
    model.component("comp1").physics("ewfd").feature("sctr1").selection().named("sel_open");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").label("paper-seeded wave-optics mesh");
    model.component("comp1").mesh("mesh1").automatic(false);
    model.component("comp1").mesh("mesh1").feature("size").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size").set("hmax", "mesh_bulk");
    model.component("comp1").mesh("mesh1").feature("size").set("hmin", "mesh_metal/4");
    model.component("comp1").mesh("mesh1").create("size_atoms", "Size");
    model.component("comp1").mesh("mesh1").feature("size_atoms").selection().named("sel_atoms");
    model.component("comp1").mesh("mesh1").feature("size_atoms").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size_atoms").set("hmax", "mesh_metal");
    model.component("comp1").mesh("mesh1").feature("size_atoms").set("hmin", "mesh_metal/4");

    model.study().create("std1");
    model.study("std1").label("1550 nm forward TE00 frequency-domain study");
    model.study("std1").create("freq", "Frequency");
    model.study("std1").feature("freq").set("plist", "freq0");

    model.label("guided_wave_metasurface_structure.mph");

    return model;
  }

  public static void main(String[] args) {
    Model model = run();
    model = run2(model);
    run3(model);
  }

}
