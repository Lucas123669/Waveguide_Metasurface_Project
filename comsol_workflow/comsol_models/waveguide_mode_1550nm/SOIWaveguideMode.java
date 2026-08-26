/*
 * SOIWaveguideMode.java
 */

import com.comsol.model.*;
import com.comsol.model.util.*;

/** Model exported on Aug 25 2026, 19:51 by COMSOL 6.3.0.290. */
public class SOIWaveguideMode {

  public static Model run() {
    Model model = ModelUtil.create("Model");

    model
         .modelPath("D:\\xgxz333\\workspace\\graduate\\AI4COMSOL\\Code\\comsol-workflow-master\\guided-wave-metasurface-workflow\\comsol_models\\waveguide_mode_1550nm");

    model.label("soi_waveguide_mode");
    model.label("soi_waveguide_mode.mph");

    model.param().set("lambda0", "1.55[um]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("wg_w", "0.6[um]");
    model.param().set("wg_h", "0.22[um]");
    model.param().set("box_h", "3.0[um]");
    model.param().set("air_h", "2[um]");
    model.param().set("side_pad", "1.5[um]");
    model.param().set("n_air", "1.0");
    model.param().set("n_si", "3.48");
    model.param().set("n_sio2", "1.444");
    model.param().set("xmin", "-wg_w/2-side_pad");
    model.param().set("xmax", "wg_w/2+side_pad");
    model.param().set("ymin", "-box_h");
    model.param().set("ymax", "wg_h+air_h");
    model.param().set("mesh_core", "0.035[um]");
    model.param().set("mesh_clad", "0.15[um]");
    model.param().set("tol", "1[nm]");

    model.component().create("comp1", true);

    model.component("comp1").label("SOI waveguide cross section");

    model.component("comp1").geom().create("geom1", 2);
    model.component("comp1").geom("geom1").lengthUnit("um");
    model.component("comp1").geom("geom1").create("air_window", "Rectangle");
    model.component("comp1").geom("geom1").feature("air_window").label("air computational window");
    model.component("comp1").geom("geom1").feature("air_window").set("base", "corner");
    model.component("comp1").geom("geom1").feature("air_window").set("pos", new String[]{"xmin", "ymin"});
    model.component("comp1").geom("geom1").feature("air_window").set("size", new String[]{"xmax-xmin", "ymax-ymin"});
    model.component("comp1").geom("geom1").feature("air_window").set("selresult", true);
    model.component("comp1").geom("geom1").create("box", "Rectangle");
    model.component("comp1").geom("geom1").feature("box").label("3 um buried oxide");
    model.component("comp1").geom("geom1").feature("box").set("base", "corner");
    model.component("comp1").geom("geom1").feature("box").set("pos", new String[]{"xmin", "ymin"});
    model.component("comp1").geom("geom1").feature("box").set("size", new String[]{"xmax-xmin", "box_h"});
    model.component("comp1").geom("geom1").feature("box").set("selresult", true);
    model.component("comp1").geom("geom1").create("core", "Rectangle");
    model.component("comp1").geom("geom1").feature("core").label("600 nm x 220 nm silicon ridge");
    model.component("comp1").geom("geom1").feature("core").set("base", "corner");
    model.component("comp1").geom("geom1").feature("core").set("pos", new String[]{"-wg_w/2", "0"});
    model.component("comp1").geom("geom1").feature("core").set("size", new String[]{"wg_w", "wg_h"});
    model.component("comp1").geom("geom1").feature("core").set("selresult", true);
    model.component("comp1").geom("geom1").feature("fin").set("action", "union");
    model.component("comp1").geom("geom1").run();

    model.component("comp1").selection().create("sel_left", "Box");
    model.component("comp1").selection("sel_left").geom("geom1", 1);
    model.component("comp1").selection("sel_left").set("condition", "inside");
    model.component("comp1").selection("sel_left").set("xmin", "xmin");
    model.component("comp1").selection("sel_left").set("xmax", "xmin+tol");
    model.component("comp1").selection("sel_left").set("ymin", "ymin");
    model.component("comp1").selection("sel_left").set("ymax", "ymax");
    model.component("comp1").selection().create("sel_right", "Box");
    model.component("comp1").selection("sel_right").geom("geom1", 1);
    model.component("comp1").selection("sel_right").set("condition", "inside");
    model.component("comp1").selection("sel_right").set("xmin", "xmax-tol");
    model.component("comp1").selection("sel_right").set("xmax", "xmax");
    model.component("comp1").selection("sel_right").set("ymin", "ymin");
    model.component("comp1").selection("sel_right").set("ymax", "ymax");
    model.component("comp1").selection().create("sel_bottom", "Box");
    model.component("comp1").selection("sel_bottom").geom("geom1", 1);
    model.component("comp1").selection("sel_bottom").set("condition", "inside");
    model.component("comp1").selection("sel_bottom").set("xmin", "xmin");
    model.component("comp1").selection("sel_bottom").set("xmax", "xmax");
    model.component("comp1").selection("sel_bottom").set("ymin", "ymin");
    model.component("comp1").selection("sel_bottom").set("ymax", "ymin+tol");
    model.component("comp1").selection().create("sel_top", "Box");
    model.component("comp1").selection("sel_top").geom("geom1", 1);
    model.component("comp1").selection("sel_top").set("condition", "inside");
    model.component("comp1").selection("sel_top").set("xmin", "xmin");
    model.component("comp1").selection("sel_top").set("xmax", "xmax");
    model.component("comp1").selection("sel_top").set("ymin", "ymax-tol");
    model.component("comp1").selection("sel_top").set("ymax", "ymax");
    model.component("comp1").selection().create("sel_outer", "Union");
    model.component("comp1").selection("sel_outer").geom("geom1", 1);
    model.component("comp1").selection("sel_outer")
         .set("input", new String[]{"sel_left", "sel_right", "sel_bottom", "sel_top"});

    model.component("comp1").material().create("mat_air", "Common");
    model.component("comp1").material("mat_air").label("Air");
    model.component("comp1").material("mat_air").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_air").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_air", "0", "0", "0", "n_air", "0", "0", "0", "n_air"});
    model.component("comp1").material("mat_air").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});
    model.component("comp1").material().create("mat_sio2", "Common");
    model.component("comp1").material("mat_sio2").label("Silicon dioxide");
    model.component("comp1").material("mat_sio2").selection().named("geom1_box_dom");
    model.component("comp1").material("mat_sio2").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_sio2").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_sio2", "0", "0", "0", "n_sio2", "0", "0", "0", "n_sio2"});
    model.component("comp1").material("mat_sio2").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});
    model.component("comp1").material().create("mat_si", "Common");
    model.component("comp1").material("mat_si").label("Silicon");
    model.component("comp1").material("mat_si").selection().named("geom1_core_dom");
    model.component("comp1").material("mat_si").propertyGroup()
         .create("RefractiveIndex", "RefractiveIndex", "Refractive index");
    model.component("comp1").material("mat_si").propertyGroup("RefractiveIndex")
         .set("n", new String[]{"n_si", "0", "0", "0", "n_si", "0", "0", "0", "n_si"});
    model.component("comp1").material("mat_si").propertyGroup("RefractiveIndex")
         .set("ki", new String[]{"0", "0", "0", "0", "0", "0", "0", "0", "0"});

    model.component("comp1").physics().create("ewfd", "ElectromagneticWavesFrequencyDomain", "geom1");
    model.component("comp1").physics("ewfd").create("sctr1", "Scattering", 1);
    model.component("comp1").physics("ewfd").feature("sctr1").selection().named("sel_outer");

    model.component("comp1").mesh().create("mesh1");
    model.component("comp1").mesh("mesh1").automatic(false);
    model.component("comp1").mesh("mesh1").feature("size").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size").set("hmax", "mesh_clad");
    model.component("comp1").mesh("mesh1").feature("size").set("hmin", "mesh_core/5");
    model.component("comp1").mesh("mesh1").create("size_core", "Size");
    model.component("comp1").mesh("mesh1").feature("size_core").selection().named("geom1_core_dom");
    model.component("comp1").mesh("mesh1").feature("size_core").set("custom", "on");
    model.component("comp1").mesh("mesh1").feature("size_core").set("hmax", "mesh_core");
    model.component("comp1").mesh("mesh1").feature("size_core").set("hmin", "mesh_core/5");

    model.study().create("std1");
    model.study("std1").create("mode", "ModeAnalysis");
    model.study("std1").feature("mode").label("1550 nm guided-mode analysis");
    model.study("std1").feature("mode").set("modeFreq", "freq0");
    model.study("std1").feature("mode").set("neigs", "6");
    model.study("std1").feature("mode").set("shift", "2.5");

    model.component("comp1").mesh("mesh1").run();

    model.study("std1").run();

    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "real(ewfd.neff)");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").computeResult();
    model.result().numerical().remove("gev1");
    model.result().numerical().create("eva1", "Eval");
    model.result().numerical().remove("eva1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("expr", "imag(ewfd.neff)");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").computeResult();
    model.result().numerical().remove("gev1");

    return model;
  }

  public static void main(String[] args) {
    run();
  }

}
