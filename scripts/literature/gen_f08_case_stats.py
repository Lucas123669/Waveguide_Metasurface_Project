# -*- coding: utf-8 -*-
"""Generate docs/reports/literature/2026-09-02_F08制造案例统计与汇报.md.

Data source : F08 = Yang et al., Advanced manufacturing of dielectric meta-devices,
              Photonics Insights 3(2), R04 (2024) - cases extracted from the full text.
Statistics  : technical group / technique family / function / material / band.
Run         : python scripts/literature/gen_f08_case_stats.py
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

OUT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", "docs", "reports", "literature",
                                    "2026-09-02_F08制造案例统计与汇报.md"))

# ------------------- case registry (data) -------------------
CASES = [
# ---------------- 3.1.1 EBL ----------------
dict(id="C01", grp="standard", tech="EBL", author="Yang 2020", ref="[28]",
     mat="Si-on-sapphire", mats=["Si"], func="structural color", funcs=["structural color"],
     band="visible", fig="Fig.4(a,b)",
     metric="三色纳米盘 D/P: 170/320, 90/200, 160/300 nm; 粗糙度<10 nm; 色域 181.8% sRGB",
     note="PMMA->Cr hard-mask lift-off -> CHF3/SF6 RIE"),
dict(id="C02", grp="standard", tech="EBL", author="Gao 2018", ref="[22]",
     mat="Si (C-shaped)", mats=["Si"], func="nonlinear hologram", funcs=["hologram"],
     band="visible", fig="Fig.4(c)",
     metric="C 形 Si 纳米天线; 高效青/蓝 THG 全息",
     note="THG=third-harmonic generation"),
dict(id="C03", grp="standard", tech="EBL", author="Wan 2022", ref="[150]",
     mat="Si", mats=["Si"], func="vectorial hologram", funcs=["hologram"],
     band="visible", fig="Fig.4(d)",
     metric="Si 矩形柱, RIE 后侧壁近 90°; 可调全彩矢量全息",
     note="metamolecules"),
dict(id="C04", grp="standard", tech="EBL", author="Devlin 2016 / Khorasaninejad 2016", ref="[67,15]",
     mat="TiO2 (ALD)", mats=["TiO2"], func="metalens", funcs=["metalens"],
     band="visible", fig="Fig.4(e,f)",
     metric="粗糙度<1 nm; 可见 metalens 效率 86%",
     note="EBL 负结构 + ALD 填 TiO2 + 反向 RIE (Cl2/BCl3)"),
dict(id="C05", grp="standard", tech="EBL", author="Sun 2017", ref="[30]",
     mat="TiO2 (EB evap)", mats=["TiO2"], func="structural color", funcs=["structural color"],
     band="visible", fig="Fig.4(g)",
     metric="全彩打印; 粗糙度 0.66 nm; lift-off 截面梯形->RIE 获 89-90° 垂直侧壁",
     note="EBL + 电子束蒸发 + lift-off"),
dict(id="C06", grp="standard", tech="EBL", author="Wang 2018", ref="[12]",
     mat="GaN", mats=["GaN"], func="metalens", funcs=["metalens"],
     band="visible", fig="Fig.4(i)",
     metric="宽带消色差 metalens (可见); 集成共振单元设计 (top-down EBL+etch)",
     note="Tsai 组"),
dict(id="C07", grp="standard", tech="EBL", author="Chen 2017", ref="[151]",
     mat="GaN", mats=["GaN"], func="metalens", funcs=["metalens"],
     band="visible", fig="Fig.4(j)",
     metric="像素级全彩 GaN metalens (on-axis focusing, 集成于 CMOS image sensor); 效率 50.6-91.6% (F08 Sec.5 汇总)",
     note="Chen 2017"),
# ---------------- 3.1.2 FIB ----------------
dict(id="C08", grp="standard", tech="FIB", author="Garg 2018", ref="[165]",
     mat="Si", mats=["Si"], func="structural color", funcs=["structural color"],
     band="visible", fig="Fig.5(a)",
     metric="Ga 高斯束直写纳米孔, 变径多色; 孔呈锥形",
     note="单步无掩模"),
dict(id="C09", grp="standard", tech="FIB", author="Gorkunov 2018", ref="[166]",
     mat="m-Si on sapphire", mats=["Si"], func="chirality", funcs=["chirality"],
     band="visible", fig="Fig.5(b)",
     metric="4 重旋转对称手性超表面; 可见透明+强手性",
     note="FIB 数字直写"),
dict(id="C10", grp="standard", tech="FIB", author="Karvounis 2016", ref="[167]",
     mat="GST", mats=["GST"], func="tunable/phase-change", funcs=["tunable"],
     band="NIR", fig="Fig.5(c)",
     metric="GST 纳米光栅; 相变可切换 NIR 超表面",
     note="Ge2Sb2Te5"),
dict(id="C11", grp="standard", tech="FIB", author="Semmlinger 2018", ref="[168]",
     mat="ZnO", mats=["ZnO"], func="nonlinear/VUV", funcs=["nonlinear"],
     band="UV/VUV", fig="Fig.5(d)",
     metric="FIB 铣 ZnO 超表面, 相干真空紫外 197 nm 产生",
     note="VUV generation"),
dict(id="C12", grp="standard", tech="FIB", author="Karvounis (2016)", ref="[169]",
     mat="Si membrane / ITO", mats=["Si"], func="modulator", funcs=["modulator"],
     band="optical", fig="Fig.5(e)",
     metric="纳米悬臂阵列, 亚 GHz 光学调制",
     note="nanomechanically reconfigurable"),
dict(id="C13", grp="standard", tech="FIB", author="Khan 2022", ref="[170]",
     mat="Nb2O5/SiO2", mats=["Nb2O5"], func="waveguide photonic crystal", funcs=["waveguide"],
     band="optical", fig="Fig.5(f)",
     metric="对称平板波导光子晶体 Fano filter",
     note="优化束流/剂量/循环数"),
dict(id="C14", grp="standard", tech="FIB", author="Bermudez-Urena 2019", ref="[171]",
     mat="SiO2/Au", mats=["SiO2"], func="3D multilayer", funcs=["multilayer"],
     band="optical", fig="Fig.5(g)",
     metric="自卷多层超表面 (SiO2/Au)",
     note="stress-induced self-rolling"),
dict(id="C15", grp="standard", tech="FIB", author="Tseng 2019", ref="[172]",
     mat="Si3N4/Au", mats=["Si3N4"], func="3D chirality", funcs=["chirality"],
     band="optical", fig="Fig.5(h)",
     metric="3D 阿基米德螺旋手性超表面; 自由站立 Au/Si3N4 双层",
     note="Ga FIB 铣削"),
# ---------------- 3.1.3 laser: LIL ----------------
dict(id="C16", grp="standard", tech="LIL", author="Chen 2018", ref="[199]",
     mat="HfO2", mats=["HfO2"], func="grating", funcs=["grating"],
     band="visible", fig="Fig.6(b)",
     metric="2D 衍射光栅, 偏振无关高衍射效率 (HfO2, 紫外材料)",
     note="两次正交曝光 + 离子束刻蚀"),
dict(id="C17", grp="standard", tech="LIL", author="Seo 2013", ref="[200]",
     mat="Si (SOI)", mats=["Si"], func="reflector", funcs=["reflector"],
     band="broadband", fig="Fig.6(c)",
     metric="大面积印刷 Si 孔阵列宽带膜反射器",
     note=""),
dict(id="C18", grp="standard", tech="LIL", author="Berzins 2020", ref="[93]",
     mat="a-Si/p-Si", mats=["Si"], func="Mie metasurface", funcs=["Mie resonators"],
     band="visible", fig="Fig.6(d)",
     metric="单脉冲四束 LIL (300 ps, 532 nm): a-Si 膜直接熔成 Mie 纳米颗粒/p-Si 纳米孔",
     note="high-throughput direct patterning"),
dict(id="C19", grp="standard", tech="LIL", author="Kamali 2019", ref="[201]",
     mat="photoresist (3D)", mats=["polymer"], func="3D patterning", funcs=["3D patterning"],
     band="visible", fig="Fig.6(e)",
     metric="超表面掩模辅助 LIL; diamond metamask 产生 3D 光场图案",
     note="514 nm 照明"),
# ---------------- 3.1.3 laser: LDW ----------------
dict(id="C20", grp="standard", tech="LDW", author="Huang 2022", ref="[205]",
     mat="Si/Cr on fused silica", mats=["Si"], func="metasurface array", funcs=["grating"],
     band="NIR", fig="Fig.7(a)",
     metric="图案化脉冲 LDW (520 nm fs) 直写 H 形亚波长单元, 后蚀刻",
     note="SLM 相位掩模"),
dict(id="C21", grp="standard", tech="LDW", author="Bochek 2021", ref="[206]",
     mat="GST", mats=["GST"], func="tunable metasurface", funcs=["tunable"],
     band="NIR", fig="Fig.7(b)",
     metric="780 nm 激光直写 GST 可调超表面 (玻璃/蓝宝石)",
     note=""),
dict(id="C22", grp="standard", tech="LDW", author="Wang 2023", ref="[207]",
     mat="laser-induced graphene", mats=["graphene"], func="THz complex-amplitude metasurface", funcs=["beam shaping"],
     band="THz", fig="Fig.7(c)",
     metric="15x15 mm2 C 形石墨烯天线复振幅调制超表面, 一步激光写 34 s",
     note="THz optical pattern recognition"),
dict(id="C23", grp="standard", tech="LDW", author="Lu 2023", ref="[208]",
     mat="PdO2-x / CdS", mats=["CdS"], func="chiral 3D growth", funcs=["chirality"],
     band="optical", fig="Fig.7(d)",
     metric="矢量光束偏振定向手性生长螺旋纳米结构",
     note="CW 激光诱导"),
# ---------------- 3.1.3 laser: two-photon LDW ----------------
dict(id="C24", grp="standard", tech="2PP-LDW", author="Rybin 2016", ref="[209]",
     mat="photoresist (polymer)", mats=["polymer"], func="photonic crystal/metasurface", funcs=["diffraction"],
     band="visible", fig="Fig.8(a)",
     metric="C4v/C6v 晶格超表面及反结构; 多阶衍射->零阶衍射转变",
     note="780 nm fs 双光子"),
dict(id="C25", grp="standard", tech="2PP-LDW", author="Zhan 2019", ref="[210]",
     mat="polymer (2PP)", mats=["polymer"], func="3D field control", funcs=["3D patterning"],
     band="visible", fig="Fig.8(b)",
     metric="逆向设计球形 Mie 散射体阵列控制 3D 光场",
     note="inverse Mie scattering"),
dict(id="C26", grp="standard", tech="2PP-LDW", author="Wei 2019", ref="[211]",
     mat="polymer (2PP)", mats=["polymer"], func="polarization beamsplitter", funcs=["beam shaping"],
     band="NIR", fig="Fig.8(c)",
     metric="逆向设计自由形态 NIR 偏振分束器 3D 打印",
     note="layer-by-layer 3D print on fused silica"),
dict(id="C27", grp="standard", tech="2PP-LDW", author="Plidschun 2022", ref="[214]",
     mat="polymer (2PP)", mats=["polymer"], func="hologram on fiber", funcs=["hologram"],
     band="visible", fig="Fig.8(d)",
     metric="单模光纤端面多焦点全息 (直径 20 um 尺度)",
     note="fiber facet nanopatterning"),
dict(id="C28", grp="standard", tech="2PP-LDW", author="Hadibrata 2021", ref="[215]",
     mat="polymer (2PP)", mats=["polymer"], func="metalens on fiber", funcs=["metalens"],
     band="visible", fig="Fig.8(f)",
     metric="光纤尖端 metalens (环形光栅), objective-first 逆向设计 + 双光子打印",
     note="homebuilt 2PP 系统验证 'NU' 图案"),
dict(id="C29", grp="standard", tech="2PP-LDW", author="Faniayeu 2017", ref="[216]",
     mat="polymer helix + metal", mats=["polymer"], func="perfect absorber", funcs=["absorber"],
     band="MIR", fig="Fig.8(e)",
     metric="3D 螺旋完美吸收器; 6-11 um 峰值吸收>80%",
     note="helix-based IR absorber"),
# ---------------- 3.2.1 grayscale ----------------
dict(id="C30", grp="advanced", tech="grayscale", author="Geng 2023", ref="[233]",
     mat="TiO2 (ALD fill)", mats=["TiO2"], func="structural color", funcs=["structural color"],
     band="visible", fig="Fig.9(a)",
     metric="EBL 灰度变深度孔 + ALD 填 TiO2 -> X-Y-Z 三维高度梯度纳米柱; 结构色",
     note="dose-to-depth"),
dict(id="C31", grp="advanced", tech="grayscale", author="Hentschel 2023", ref="[234]",
     mat="Si", mats=["Si"], func="color printing (Mie void)", funcs=["structural color"],
     band="visible", fig="Fig.9(b)",
     metric="FIB 灰度 Mie void: 等径变深/变径变深; 彩印",
     note="conical Mie voids"),
dict(id="C32", grp="advanced", tech="grayscale", author="Wang 2021", ref="[236]",
     mat="low-index polymer (2PP)", mats=["polymer"], func="color printing", funcs=["structural color"],
     band="visible", fig="Fig.9(c)",
     metric="双光子灰度低折射率纳米柱: 高度/周期/直径同变; 全彩灰度画",
     note="3D printed low-index nanopillars"),
dict(id="C33", grp="advanced", tech="grayscale", author="Williams 2019", ref="[237]",
     mat="dielectric + MIM cavities", mats=["dielectric"], func="multispectral filter array", funcs=["filter"],
     band="visible-NIR", fig="Fig.9(d)",
     metric="EBL 灰度(小批量)+UV 二元掩模灰度(大批量) MIM Fabry-Perot 滤光阵列",
     note="dose 控腔厚"),
# ---------------- 3.2.2 multistep ----------------
dict(id="C34", grp="advanced", tech="multistep", author="Lu 2022", ref="[238]",
     mat="Si", mats=["Si"], func="self-cleaning + dynamic color", funcs=["multifunctional"],
     band="visible", fig="Fig.10(a)",
     metric="两步(EBL Cr 掩模 + 激光光刻) Si 超表面: 超浸润自清洁 + 动态颜色",
     note="two-step lithography"),
dict(id="C35", grp="advanced", tech="multistep", author="Zhao 2021", ref="[221]",
     mat="a-Si + Al mask", mats=["Si"], func="synthetic-aperture metalens", funcs=["metalens"],
     band="NIR", fig="Fig.10(b)",
     metric="合成孔径 metalens: EBL 做 a-Si 柱 + 光刻做 Al 挡光层",
     note="EBL + photolithography"),
dict(id="C36", grp="advanced", tech="multistep", author="Guo 2016", ref="[222]",
     mat="Au nanorod + Si nanodisk", mats=["Si"], func="hybrid metal-dielectric", funcs=["hybrid"],
     band="visible", fig="Fig.10(c)",
     metric="两步 EBL + 精确对准: Au 纳米棒与 Si 纳米盘混合, 多极耦合",
     note="cross-shaped Au alignment marks"),
# ---------------- 3.2.3 SPL ----------------
dict(id="C37", grp="advanced", tech="SPL", author="Lisunova 2017", ref="[240]",
     mat="Si (PPA thermal SPL)", mats=["Si"], func="high-AR patterning", funcs=["high AR"],
     band="structural", fig="Fig.11(b)",
     metric="热 SPL (PPA 自放大解聚) + SiO2 掩模 + deep RIE; 侧壁 87±2°",
     note="thermal SPL + dry etch"),
dict(id="C38", grp="advanced", tech="SPL", author="Zhang 2023", ref="[241]",
     mat="VO2", mats=["VO2"], func="tunable reflector", funcs=["tunable"],
     band="near/MIR", fig="Fig.11(c)",
     metric="电场 SPL 逐层刻 VO2 (负偏压+超声); VO2-Au 可调反射超表面",
     note="electric-field SPL"),
# ---------------- 3.3.1 UV lithography ----------------
dict(id="C39", grp="large-scale", tech="UV(i-line)", author="She 2018", ref="[267]",
     mat="Si", mats=["Si"], func="metalens", funcs=["metalens"],
     band="NIR", fig="Fig.12(a)",
     metric="i-line 365 nm stepper: 2 cm 直径 Si NIR metalens, 衍射极限聚焦",
     note="大波长限制可见光小特征"),
dict(id="C40", grp="large-scale", tech="UV(KrF)", author="Leitis 2021", ref="[269]",
     mat="Ge + Al2O3 membrane", mats=["Ge"], func="MIR metasurfaces/biosensing", funcs=["sensing"],
     band="MIR", fig="Fig.12(b)",
     metric="4 英寸 Si 晶圆 KrF 248 nm 加工 Ge 超表面 + 透明 Al2O3 膜; 中红外/生物传感",
     note="wafer-scale cost-effective"),
dict(id="C41", grp="large-scale", tech="UV(KrF)", author="Park 2019", ref="[268]",
     mat="glass (SiO2)", mats=["SiO2"], func="metalens", funcs=["metalens"],
     band="visible", fig="Fig.12(c)",
     metric="KrF DUV 投影光刻 全玻璃厘米级可见 metalens (1 cm, 4 英寸 SiO2 晶圆)",
     note="即本库 F-09"),
dict(id="C42", grp="large-scale", tech="UV(ArF)", author="Xu 2019", ref="[270]",
     mat="Si (nanopyramid)", mats=["Si"], func="polarizing bandpass filter", funcs=["filter"],
     band="SWIR", fig="Fig.12(d)",
     metric="12 英寸晶圆 ArF 193 nm immersion + ICP-RIE: Si 纳米金字塔偏振带通滤波 (MPW@IME)",
     note="short-wave IR polarization"),
dict(id="C43", grp="large-scale", tech="UV(ArF)", author="Li 2019 / Xu 2021", ref="[100,271]",
     mat="a-Si on glass", mats=["Si"], func="subtractive color filter", funcs=["filter"],
     band="visible", fig="Fig.12(e)",
     metric="12 英寸玻璃晶圆减色滤光阵列 (CMOS 平台, 胶辅助层转移)",
     note="layer transfer Si->glass"),
dict(id="C44", grp="large-scale", tech="UV(ArF)", author="Hu 2020", ref="[272]",
     mat="a-Si on glass", mats=["Si"], func="metalens", funcs=["metalens"],
     band="NIR (940 nm)", fig="Fig.12(f)",
     metric="12 英寸玻璃晶圆 a-Si 940 nm 指纹成像 metalens",
     note="CMOS-compatible"),
dict(id="C45", grp="large-scale", tech="UV(KrF)", author="Park 2024", ref="[136]",
     mat="glass (fused silica)", mats=["SiO2"], func="metalens (astronomy)", funcs=["metalens"],
     band="visible", fig="Fig.12(g)",
     metric="100 mm 直径全玻璃可见 metalens; 直接天文成像 (月球)",
     note="KrF DUV projection"),
# ---------------- 3.3.2 NIL ----------------
dict(id="C46", grp="large-scale", tech="NIL", author="Yao & Wu 2017", ref="[279]",
     mat="a-Si/Si3N4/SiO2", mats=["Si"], func="ultra-broadband reflector", funcs=["reflector"],
     band="broadband", fig="Fig.13(a)",
     metric="异质全介质超宽带反射器; NIL 图案 -> Cr 掩模 -> RIE",
     note=""),
dict(id="C47", grp="large-scale", tech="NIL(soft)", author="Cao 2022", ref="[280]",
     mat="Si (SU-8 resist)", mats=["Si"], func="geometry tuning", funcs=["fabrication method"],
     band="structural", fig="Fig.13(b)",
     metric="软 NIL + 可控 RIE: SU-8 图案精确转 Si, 调 meta-atom 几何",
     note="soft NIL"),
dict(id="C48", grp="large-scale", tech="NIL(UV)", author="Yoon 2020", ref="[281]",
     mat="TiO2 nanoparticle resin (PER)", mats=["TiO2"], func="metalens", funcs=["metalens"],
     band="visible", fig="Fig.13(c)",
     metric="TiO2 纳米颗粒 UV 树脂一步 UV-NIL hierarchical metalens (无沉积/刻蚀)",
     note="plum-pudding metalens"),
dict(id="C49", grp="large-scale", tech="NIL(UV)", author="Kim 2022", ref="[126]",
     mat="TiO2 nano-PER", mats=["TiO2"], func="metahologram", funcs=["hologram"],
     band="visible", fig="Fig.13(d)",
     metric="一步 NIL TiO2 nano-PER 全息; 效率纪录 90.6%; 可转印 PC/PP/曲面玻璃",
     note="highest-efficiency hologram"),
dict(id="C50", grp="large-scale", tech="NIL(PVA wet)", author="Choi 2023", ref="[282]",
     mat="TiO2 PER", mats=["TiO2"], func="high-AR metalens", funcs=["metalens"],
     band="visible", fig="Fig.13(e)",
     metric="PVA 水溶模湿法溶解脱模; 无缺陷高深宽比复制",
     note="避免脱模剪切应力"),
dict(id="C51", grp="large-scale", tech="NIL(multilayer)", author="Quan 2023", ref="[283]",
     mat="ZnO (SPE growth)", mats=["ZnO"], func="high-AR metalens", funcs=["metalens"],
     band="visible", fig="Fig.13(f)",
     metric="多层 NIL + 溶液相外延 (SPE): 高深宽比 ZnO 纳米柱 metalens",
     note="OrmoStamp thermal NIL"),
# ---------------- 3.3.3 self-assembly ----------------
dict(id="C52", grp="large-scale", tech="self-assembly(nanosphere)", author="Zhang 2017", ref="[285]",
     mat="Si on PET", mats=["Si"], func="flexible sensing metasurface", funcs=["sensing"],
     band="NIR", fig="Fig.14(a)",
     metric="PS 球自组装 + 两次 RIE: 柔性 PET 上 Si 柱超表面 (传感)",
     note="flexible + sensing"),
dict(id="C53", grp="large-scale", tech="self-assembly(nanosphere)", author="Moitra 2015", ref="[98]",
     mat="Si on SOI", mats=["Si"], func="perfect reflector", funcs=["reflector"],
     band="broadband", fig="Fig.14(b)",
     metric="纳米球光刻大面积 Si 柱完美反射器; PS 820->560 nm",
     note="large-scale all-dielectric"),
dict(id="C54", grp="large-scale", tech="self-assembly(grayscale)", author="Zheng 2021", ref="[232]",
     mat="Si nanospheres", mats=["Si"], func="metalens", funcs=["metalens"],
     band="NIR (1.7 um)", fig="Fig.14(c)",
     metric="灰度纳米球光刻 + DMD 投影 (365 nm): 非周期相位 metalens 1.7 um, 相对效率>83%",
     note="scalable nonperiodic phase"),
dict(id="C55", grp="large-scale", tech="self-assembly(dewetting)", author="Das Gupta 2019", ref="[286]",
     mat="high-index glass", mats=["glass"], func="self-assembled metasurface", funcs=["fabrication method"],
     band="visible", fig="Fig.14(d)",
     metric="模板化流体失稳(dewetting): 玻璃纳米颗粒 ~100 nm, 间距小至 10 nm; 20x11 cm2",
     note="EPFL logo demo"),
dict(id="C56", grp="large-scale", tech="self-assembly(AAO)", author="Du 2021", ref="[287]",
     mat="TiO2 (AAO template)", mats=["TiO2"], func="large-area metasurface", funcs=["fabrication method"],
     band="visible", fig="(text)",
     metric="AAO 模板 + TiO2 大面积超表面",
     note="anodized aluminum oxide template"),
# ---------------- 4.1 multilayer ----------------
dict(id="C57", grp="extreme", tech="multilayer", author="Tanaka 2020", ref="[303]",
     mat="Si (bilayer)", mats=["Si"], func="chiral bilayer", funcs=["chirality"],
     band="visible", fig="Fig.15(a)",
     metric="双层手性 Si 超表面; 圆二色纪录 CD=0.7",
     note="two-step EBL"),
dict(id="C58", grp="extreme", tech="multilayer", author="Deng 2022", ref="[103]",
     mat="a-Si + Ag", mats=["Si"], func="full-space manipulation", funcs=["hologram"],
     band="visible", fig="Fig.15(b)",
     metric="a-Si/Ag 双砖双层超表面; 透/反空间独立相位操纵 (meta-hologram)",
     note="overlay EBL"),
dict(id="C59", grp="extreme", tech="multilayer", author="Zhou 2018", ref="[307]",
     mat="a-Si in PDMS", mats=["Si"], func="multiwavelength metalens", funcs=["metalens"],
     band="multi", fig="Fig.15(c)",
     metric="PDMS 封层堆叠多层非相互作用超表面; 多波长独立相位 (metalens doublet)",
     note="Ge 牺牲层转移"),
dict(id="C60", grp="extreme", tech="multilayer(2PP)", author="Balli 2020", ref="[304]",
     mat="polymer (2PP)", mats=["polymer"], func="achromatic metalens", funcs=["metalens"],
     band="NIR (1000-1800 nm)", fig="Fig.15(d)",
     metric="双光子打印混合消色差 metalens (相位板+柱); 1000-1800 nm 宽带",
     note="hybrid achromatic"),
dict(id="C61", grp="extreme", tech="multilayer(3D print)", author="Pan 2023", ref="[305]",
     mat="polymer (3D print)", mats=["polymer"], func="multilayer achromatic metalens", funcs=["metalens"],
     band="visible-NIR", fig="Fig.15(e)",
     metric="3D 打印高 NA 多层消色差 metalens (单/双/三层)",
     note="MAM"),
dict(id="C62", grp="extreme", tech="multilayer(3D print)", author="Roques-Carmes 2022", ref="[306]",
     mat="low-index polymer", mats=["polymer"], func="inverse-designed metaoptics", funcs=["beam shaping"],
     band="NIR", fig="Fig.15(f)",
     metric="3D 打印逆向设计多层 meta-optics (低折射率聚合物, 拓扑优化+全波)",
     note="two-photon polymerization"),
# ---------------- 4.2 flexible ----------------
dict(id="C63", grp="extreme", tech="flexible", author="Zhang 2019", ref="[308]",
     mat="TiO2 in PDMS", mats=["TiO2"], func="stretchable metasurface", funcs=["flexible"],
     band="visible", fig="Fig.16(a)",
     metric="PDMS 嵌 TiO2 可拉伸全谱偏振不敏感超表面 (Cu/SU-8/Cu 牺牲衬底转移)",
     note="mechanical tunability"),
dict(id="C64", grp="extreme", tech="flexible", author="Kamali 2016", ref="[309]",
     mat="Si in PDMS", mats=["Si"], func="tunable metalens", funcs=["metalens"],
     band="visible", fig="Fig.16(b)",
     metric="弹性 Si 纳米柱/PDMS 可调微透镜; 焦距 600->1400 um",
     note="highly tunable elastic lens"),
dict(id="C65", grp="extreme", tech="flexible", author="Kamali 2016", ref="[102]",
     mat="Si in PDMS", mats=["Si"], func="conformal flexible metasurface", funcs=["flexible"],
     band="visible", fig="Fig.16(c)",
     metric="共形柔性 Si/PDMS 超表面贴合凸/凹玻璃; 光学功能与几何解耦",
     note="conformal"),
dict(id="C66", grp="extreme", tech="flexible(NIL)", author="Kim 2019", ref="[253]",
     mat="dielectric (nanocast)", mats=["dielectric"], func="flexible replication", funcs=["flexible"],
     band="visible", fig="Fig.16(d)",
     metric="纳米铸造 NIL sub-100 nm 分辨率; 复制到柔性基底 (免等离子/溶剂)",
     note="soft nanoimprint, flexible"),
# ---------------- 4.3 slanted ----------------
dict(id="C67", grp="extreme", tech="slanted", author="Chen 2023", ref="[84]",
     mat="TiO2", mats=["TiO2"], func="intrinsic chiral BIC", funcs=["chirality"],
     band="visible", fig="Fig.17(a)",
     metric="倾斜扰动超表面固有手性 BIC: CD=0.93, Q>2663 (可见); 斜刻蚀系统+Al2O3 离子准直器",
     note="面内形变角 alpha + 面外斜角 phi 联合破缺镜像对称; Nature 613, 474"),
dict(id="C68", grp="extreme", tech="slanted", author="Liu 2023", ref="[104]",
     mat="TiO2", mats=["TiO2"], func="large-angle refraction", funcs=["grating"],
     band="visible", fig="Fig.17(b)",
     metric="倾斜 TiO2 光栅大角度反常折射 80°; 相对 98.5%/绝对 89.5% (优化后 94.0%/83.6%)",
     note="正文两处数据: 80°-steering; 斜铝夹具+顶铝网抑场弯曲"),
# ---------------- 4.4 high-aspect-ratio ----------------
dict(id="C69", grp="extreme", tech="high_AR", author="Wang 2021", ref="[101]",
     mat="TiO2 (EB evap)", mats=["TiO2"], func="achromatic metalens", funcs=["metalens"],
     band="NIR (650-1000 nm)", fig="Fig.4(h)/Fig.18(a)",
     metric="1.5 um 高 TiO2 柱 89-90° 垂直侧壁; 消色差 metalens 650-1000 nm, 效率 77.1-88.5%, NA 0.24-0.1",
     note="同一工作跨 3.1.1 与 4.4 出现, 去重计数一次"),
dict(id="C70", grp="extreme", tech="high_AR(NIL)", author="Einck 2021", ref="[310]",
     mat="TiO2 nanocrystal", mats=["TiO2"], func="high-AR metalens", funcs=["metalens"],
     band="visible", fig="Fig.18(b)",
     metric="NIL 一步压印 TiO2 纳米晶; 深宽比>8, CD<60 nm",
     note="additive direct imprint"),
dict(id="C71", grp="extreme", tech="high_AR(holes)", author="Lim 2021", ref="[311]",
     mat="Si membrane (5 um)", mats=["Si"], func="holey metalens", funcs=["metalens"],
     band="NIR", fig="Fig.18(c)",
     metric="5 um 自由 Si 膜深孔 metalens; 孔深宽比 ~30:1 (Bosch), 孔壁倾斜<1°",
     note="inverse-designed holey metalens"),
dict(id="C72", grp="extreme", tech="high_AR(THz)", author="Wang 2023", ref="[312]",
     mat="Si (THz)", mats=["Si"], func="THz spin-multiplexed", funcs=["beam shaping"],
     band="THz", fig="Fig.18(d)",
     metric="三层高深宽比 THz 微柱 ~20:1 (Bosch); 自旋复用高效波前控制",
     note="thick Si wafer Bosch"),
]

# one-line mentions (excluded from counts)
MENTIONS = [
    "GaAs 倾斜 metagrating 集成 VCSEL [57] (Sec.4.4 一句话提及)",
    "HfO2 深紫外 meta-optics [144] (Sec.4.4 一句话提及)",
    "ZnO SPE metalens/多层 [132] 等应用层工作(Sec.4.4/5 背景)",
]

# Band clarifications: cases whose operating band is NOT explicit in the F08
# text (or only weakly implied). They are excluded from band statistics.
BAND_FIX = {
 "C16":"未指明","C20":"未指明","C24":"未指明","C25":"未指明",
 "C27":"未指明","C28":"未指明","C35":"未指明","C36":"未指明",
 "C51":"未指明","C52":"未指明","C57":"未指明","C53":"未指明","C55":"未指明",
 "C56":"未指明","C58":"未指明","C61":"未指明",
 "C62":"未指明","C66":"未指明","C71":"未指明",
}



def eff_band(c):
    return BAND_FIX.get(c["id"], c["band"])
GROUP_CN = {
    "standard": "① 标准纳米光刻", "advanced": "② 先进纳米光刻",
    "large-scale": "③ 大规模纳米光刻", "extreme": "④ 极端制造",
}

# ---------- functional primary grouping (each case exactly one) ----------
FUNC = {
 "metalens": "metalens / 聚焦成像类",
 "hologram": "全息 / 显示成像类",
 "structural color": "结构色 / 彩色打印类",
 "filter/sensing": "滤波 / 光谱 / 传感类",
 "reflector/absorber": "反射器 / 吸收器类",
 "grating/beam": "光栅 / 分束 / 波束调控类",
 "chirality/BIC": "手性 / BIC 类",
 "tunable/modulator": "可调 / 调制类",
 "nonlinear/VUV": "非线性 / 新型光源类",
 "inverse/3D": "逆向设计 / 3D meta-optics 类",
 "process/method": "工艺方法演示类",
 "multilayer/hybrid": "多层 / 混合 / 多功能结构类",
 "flexible": "柔性 / 可拉伸类",
}
# manual primary mapping per case id (verified during full-text reading)
FUNC_MAP = {
 "C01":"structural color","C02":"hologram","C03":"hologram","C04":"metalens",
 "C05":"structural color","C06":"metalens","C07":"metalens","C08":"structural color",
 "C09":"chirality/BIC","C10":"tunable/modulator","C11":"nonlinear/VUV","C12":"tunable/modulator",
 "C13":"filter/sensing","C14":"multilayer/hybrid","C15":"chirality/BIC","C16":"grating/beam",
 "C17":"reflector/absorber","C18":"process/method","C19":"process/method","C20":"process/method",
 "C21":"tunable/modulator","C22":"grating/beam","C23":"chirality/BIC","C24":"grating/beam",
 "C25":"inverse/3D","C26":"grating/beam","C27":"hologram","C28":"metalens",
 "C29":"reflector/absorber","C30":"structural color","C31":"structural color","C32":"structural color",
 "C33":"filter/sensing","C34":"multilayer/hybrid","C35":"metalens","C36":"multilayer/hybrid",
 "C37":"process/method","C38":"tunable/modulator","C39":"metalens","C40":"filter/sensing",
 "C41":"metalens","C42":"filter/sensing","C43":"filter/sensing","C44":"metalens",
 "C45":"metalens","C46":"reflector/absorber","C47":"process/method","C48":"metalens",
 "C49":"hologram","C50":"metalens","C51":"metalens","C52":"filter/sensing",
 "C53":"reflector/absorber","C54":"metalens","C55":"process/method","C56":"process/method",
 "C57":"chirality/BIC","C58":"hologram","C59":"metalens","C60":"metalens",
 "C61":"metalens","C62":"inverse/3D","C63":"flexible","C64":"metalens",
 "C65":"flexible","C66":"flexible","C67":"chirality/BIC","C68":"grating/beam",
 "C69":"metalens","C70":"metalens","C71":"metalens","C72":"grating/beam",
}

# ---------- band primary bins (only explicitly banded cases) ----------
def band_bin(raw):
    if not raw: return None
    r = raw.lower()
    if "uv" in r: return "UV/VUV"
    if "thz" in r: return "THz"
    if "mir" in r or "mid" in r: return "中红外 MIR"
    if "swir" in r: return "短波红外 SWIR"
    if "nir" in r and "visible" in r: return "可见-NIR"
    if "nir" in r: return "近红外 NIR"
    if "940" in r: return "近红外 NIR"
    if "1000-1800" in r: return "近红外 NIR"
    if "650-1000" in r: return "可见-NIR"
    if "1.7" in r: return "近红外 NIR"
    if "visible" in r and "nir" in r: return "可见-NIR"
    if "visible" in r: return "可见"
    if "broadband" in r or "multi" in r: return "宽带/多波段"
    return None

def main():
    ids = {c["id"]: c for c in CASES}
    assert set(FUNC_MAP) == set(ids), (set(FUNC_MAP)^set(ids))
    # group counts
    from collections import Counter, OrderedDict
    grp = Counter(c["grp"] for c in CASES)
    tech = Counter(c["tech"] for c in CASES)
    func = Counter(FUNC_MAP[i] for i in ids)
    matfreq = Counter()
    for c in CASES:
        for m in c.get("mats", []) or []:
            matfreq[m] += 1
    bands = Counter()
    for c in CASES:
        b = band_bin(eff_band(c))
        if b: bands[b] += 1
    n_banded = sum(bands.values())

    L = []
    A = L.append
    A("# F08 制造技术案例统计与汇报稿")
    A("")
    A("> 报告日期：2026-09-02 ｜ 数据来源：F08 = Yang et al., *Advanced manufacturing of dielectric meta-devices*, Photonics Insights 3(2), R04 (2024)（DOI 10.3788/PI.2024.R04，40 页，开放获取，本库 `literature/Q1_工艺_L01相关/`）")
    A("> 内容：对 F08 综述正文描述的**全介质超表面制造案例**做系统提取、分类与量化统计，形成可汇报的结构化材料（统计口径见 §2；完整案例清单见附录）。")
    A("")
    A("---")
    A("")
    A("## 1. 总览结论（先讲这三句）")
    A("")
    A(f"1. **F08 正文共系统描述了 {len(CASES)} 个独立实验案例**（另有 [57] GaAs/VCSEL、[144] HfO₂-DUV 等 3 处一句话提及未计入），覆盖 4 大制造类别、15 种以上具体工艺技术。")
    A("2. 案例数量结构呈清晰的**技术生态分层**：标准光刻（EBL/FIB/激光）承担绝大多数“创新演示”（占比最高），大规模光刻（DUV/NIL/自组装）是**量产答案**（尺度纪录：100 mm 全玻璃 metalens、12 英寸晶圆流片），极端制造（多层/柔性/倾斜/高深宽比）负责**刷新物理/性能纪录**（CD 0.93、Q>2663、效率 90.6%、深宽比 30:1）。")
    A("3. 对本项目（L01 PMMA/Si₃N₄ qBIC、L02 Si/Au）最有价值的四条可迁移结论：**(a)** EBL 工艺的粗糙度天花板可达 <1 nm（TiO₂ ALD 反向填充先例），支撑“胶决定几何”的 L01 单层 PMMA 路线；(b) 灰度光刻=变剂量→变深度，与 L01/F-01 的 dose-to-depth 调 Q 同源；(c) DUV（KrF/ArF）已到 12 英寸与 100 mm 尺度，是远期量产路线；(d) 倾斜/面外破缺工艺可实现固有手性 BIC（CD 0.93、Q>2663），是 L01 未来做强偏振椭率（χ）控制的进阶选项。")
    A("")
    A("---")
    A("")
    A("## 2. 统计口径（方法学）")
    A("")
    A("- **案例定义**：正文中明确以“某作者 et al. 制备/演示了……”描述的**独立实验演示**，判据为（材料 + 结构/工艺 + 至少一个量化结果）三者齐全。")
    A("- **去重规则**：同一底层工作跨章节重复出现只计一次。例如 [101]（Wang 2021, 1.5 μm TiO₂ 高深宽比消色差 metalens）在 Sec.3.1.1（Fig.4h）与 Sec.4.4（Fig.18a）均出现，计入 1 例；自组装 [285] 与柔性 [285] 为同一工作，只计入自组装。")
    A("- **排除规则**：仅一句话提及而无实验描述的工作不计入（如 GaAs metagrating/VCSEL [57]、HfO₂ DUV optics [144]）；综述性、机理性、展望性内容不计入。")
    A("- **分类维度**：技术（F08 自身四级框架 + 具体工艺）、功能（按器件/应用主功能，一例一主类）、材料（多标签累计计数，可重复计入，因此各材料之和可大于案例总数）、波段（仅对正文明确标定波段的案例统计）。")
    A("- 全部编号（C01–C72）与出处（F08 引用号/图号）见附录，可逐例回溯复核。")
    A("")
    A("---")
    A("")
    A("## 3. 技术维度统计")
    A("")
    A("### 3.1 四大类分布")
    A("")
    A("| 类别 | 案例数 | 占比 | 说明 |")
    A("| --- | --- | --- | --- |")
    for g, cn in GROUP_CN.items():
        n = grp[g]
        A(f"| {cn} | {n} | {n/len(CASES)*100:.0f}% | 见下表 |")
    A(f"| **合计** | **{len(CASES)}** | 100% | |")
    A("")
    A("### 3.2 具体工艺分布")
    A("")
    # collapse NIL & SA rows into their families for readability
    tech_family = OrderedDict()
    family_repr = {}
    fam_map = {
      "EBL":"EBL","FIB":"FIB","LIL":"LIL(干涉光刻)","LDW":"LDW(激光直写)","2PP-LDW":"双光子 LDW(3D 打印)",
      "grayscale":"灰度光刻","multistep":"多步光刻","SPL":"扫描探针光刻 SPL",
      "UV(i-line)":"UV 光刻·i-line 365","UV(KrF)":"UV 光刻·KrF 248","UV(ArF)":"UV 光刻·ArF 193(immersion)",
      "NIL":"NIL","NIL(soft)":"NIL(软)","NIL(UV)":"NIL(UV/PER)","NIL(PVA wet)":"NIL(水溶模)","NIL(multilayer)":"NIL(多层/SPE)",
      "self-assembly(nanosphere)":"自组装·纳米球","self-assembly(grayscale)":"自组装·灰度纳米球","self-assembly(dewetting)":"自组装·dewetting 玻璃","self-assembly(AAO)":"自组装·AAO 模板",
      "multilayer":"多层·两步对准","multilayer(2PP)":"多层·双光子","multilayer(3D print)":"多层·3D 打印",
      "flexible":"柔性·转移","flexible(NIL)":"柔性·NIL","slanted":"倾斜刻蚀","high_AR":"高深宽比·RIE",
      "high_AR(NIL)":"高深宽比·NIL","high_AR(holes)":"高深宽比·孔/膜","high_AR(THz)":"高深宽比·THz",
    }
    for c in CASES:
        key = fam_map.get(c["tech"], c["tech"])
        tech_family[key] = tech_family.get(key, 0) + 1
        family_repr.setdefault(key, c["id"]+" "+c["author"])
    A("| 类别 | 工艺族 | 案例数 | 代表案例 |")
    A("| --- | --- | --- | --- |")
    cur = None
    for k, n in tech_family.items():
        g = next(c["grp"] for c in CASES if fam_map.get(c["tech"],c["tech"])==k)
        A(f"| {GROUP_CN[g] if g!=cur else ''} | {k} | {n} | {family_repr[k]} |")
        cur = g
    A("")
    A("---")
    A("")
    A("## 4. 功能与应用维度统计（一例一主类）")
    A("")
    A("| 主功能类 | 案例数 | 占比 |")
    A("| --- | --- | --- |")
    for k in FUNC:
        A(f"| {FUNC[k]} | {func[k]} | {func[k]/len(CASES)*100:.0f}% |")
    A(f"| **合计** | **{len(CASES)}** | 100% |")
    A("")
    A("> 读法：metalens/聚焦类是绝对第一大应用（约 1/4 案例），印证 F08 的观点——成像/聚焦是超表面走向产业化的第一落点；其次是结构色/显示、滤波/传感与波束调控等“平面光学”典型场景。手性/BIC 案例虽少（约 7%），但多次刷新技术纪录（CD 0.93、Q>2663），与 L01 的 qBIC 直接相关。")
    A("")
    A("---")
    A("")
    A("## 5. 材料维度统计（多标签累计）")
    A("")
    A("| 材料 | 涉及案例数 | 典型角色 |")
    A("| --- | --- | --- |")
    mat_roles = {
      "Si":"结构色/全息/metalens/深孔/THz（含 a-/p-/m-Si、SOI/SOS）",
      "TiO2":"可见/近红外高效 metalens、全彩、ALD/蒸发/PER 全工艺",
      "polymer":"双光子 3D 打印、PER 树脂、灰度低折射率柱（2PP/PDMS/SU-8）",
      "glass":"全玻璃 metalens（KrF/ArF）、dewetting 玻璃颗粒",
      "GST":"相变可重构（FIB/LDW 直写）",
      "GaN":"可见宽带消色差 metalens",
      "ZnO":"VUV 197 nm 非线性、SPE 高深宽比 metalens",
      "SiO2":"波导/夹层/全玻璃器件",
      "VO2":"电场 SPL 可调反射",
      "Si3N4":"3D 手性螺旋、超宽带反射器组成层",
      "Ge":"KrF 晶圆级中红外",
      "HfO2":"LIL 2D 光栅（UV 材料）",
      "Nb2O5":"FIB 平板波导光子晶体",
      "graphene":"激光诱导石墨烯 THz 超表面",
      "CdS":"矢量光束手性生长",
      "dielectric":"通用介质（MIM 滤光/纳米铸造等）",
    }
    for m, n in matfreq.most_common():
        A(f"| {m} | {n} | {mat_roles.get(m,'')} |")
    A("")
    A("> 读法：**Si 与 TiO₂ 是绝对双主角**（合计约占全部材料标签的一半）；Si 靠 CMOS 兼容吃下“晶圆级/量产”叙事，TiO₂ 靠可见光低损耗+高 n 吃下“高效率器件”叙事。聚合物（2PP/PER）是 3D 打印与一步 NIL 路线的主力，正在成为第三条路线。")
    A("")
    A("---")
    A("")
    A("## 6. 波段维度统计（仅明确标定波段的案例）")
    A("")
    A(f"| 波段 | 案例数 | 说明 |")
    A("| --- | --- | --- |")
    band_note = {
      "UV/VUV":"ZnO FIB 超表面 197 nm 相干 VUV 产生 (C11)",
      "可见":"结构色、可见 metalens/全息/BIC（TiO₂/Si/GaN 主导）",
      "可见-NIR":"宽带消色差透镜、多光谱滤光阵列等",
      "近红外 NIR":"940 nm 指纹、NIR metalens/消色差、GST 相变等",
      "短波红外 SWIR":"12 英寸 Si 偏振滤波（ArF, SWIR）",
      "中红外 MIR":"Ge 晶圆超表面、螺旋吸收器 6–11 μm、VO₂ 可调反射",
      "THz":"石墨烯 LDW、20:1 Si 微柱",
      "宽带/多波段":"超宽带反射器、多层多波长等",
    }
    for b, n in bands.most_common():
        A(f"| {b} | {n} | {band_note.get(b,'')} |")
    A(f"| **合计（已标定）** | **{n_banded}** | 其余案例工作波段在正文未明确（含纯几何/工艺演示），不计入 |")
    A("")
    A("---")
    A("")
    A("## 7. 关键量化指标纪录取（汇报可以直接引用的“硬数字”）")
    A("")
    A("### 7.1 效率纪录")
    A("")
    A("| 指标 | 纪录 | 案例 | 出处 |")
    A("| --- | --- | --- | --- |")
    A("| 可见全息效率 | **90.6%**（一步 NIL TiO₂ nano-PER） | Kim 2022 | C49 · F08@Fig.13(d) [126] |")
    A("| 可见 metalens 效率 | **86%** | Khorasaninejad 2016 | C04 · [15,67] |")
    A("| 可见 GaN metalens | 50.6–91.6%（Chen 2017，集成共振单元） | Chen 2017 | C07 · [151]（F08 Sec.5 汇总） |")
    A("| NIR 消色差 metalens | 650–1000 nm，77.1–88.5% | Wang 2021 | C69 · [101] |")
    A("| 1.7 μm 灰度纳米球 metalens | 相对效率 >83% | Zheng 2021 | C54 · [232] |")
    A("| 大角度反常折射 | 偏转 **80°**，相对 98.5% / 绝对 89.5%（优化后 94.0%/83.6%） | Liu 2023 | C68 · [104] |")
    A("")
    A("### 7.2 尺度/面积纪录（量产叙事）")
    A("")
    A("| 指标 | 纪录 | 案例 | 出处 |")
    A("| --- | --- | --- | --- |")
    A("| 最大 metalens | **100 mm 全玻璃可见**（直接成像月球） | Park 2024 | C45 · [136] |")
    A("| 晶圆级 | **12 英寸** Si 偏振滤波 / 减色滤光 / 940 nm a-Si metalens（ArF，CMOS 平台） | Xu/Hu/Li | C42–C44 · [270,271,272] |")
    A("| KrF 晶圆级 | 4 英寸 Ge 中红外 + Al₂O₃ 膜；4 英寸全玻璃 1 cm metalens | Leitis/Park | C40/C41 · [269,268] |")
    A("| i-line 大面积 | 2 cm NIR Si metalens（衍射极限聚焦） | She 2018 | C39 · [267] |")
    A("| 激光直写面积 | 15×15 mm² 石墨烯超表面仅 **34 s** | Wang 2023 | C22 · [207] |")
    A("| dewetting 自组装 | 20×11 cm² 玻璃超表面（EPFL logo） | Das Gupta 2019 | C55 · [286] |")
    A("")
    A("### 7.3 工艺质量纪录（几何/表面）")
    A("")
    A("| 指标 | 纪录 | 案例 | 出处 |")
    A("| --- | --- | --- | --- |")
    A("| 侧壁粗糙度 | **<1 nm**（TiO₂ ALD 反向填充）；0.66 nm（EB 蒸发 lift-off）；<10 nm（Si RIE） | Devlin/Sun/Yang | C04/C05/C01 |")
    A("| 垂直侧壁 | 89–90°（TiO₂ RIE/蒸发蚀刻） | Wang 2021 | C69 · [101] |")
    A("| SPL+刻蚀侧壁 | 87±2°（PPA 热 SPL + deep RIE） | Lisunova 2017 | C37 · [240] |")
    A("| 深宽比（孔） | **~30:1**（5 μm 自由 Si 膜深孔，Bosch，孔壁<1°） | Lim 2021 | C71 · [311] |")
    A("| 深宽比（柱） | ~20:1（THz Si 三层微柱）；TiO₂ 1.5 μm 高/AR>8（NIL CD<60 nm） | Wang/Einck | C72/C70 · [312,310] |")
    A("| 最小 CD | <60 nm（NIL 高深宽比 TiO₂）；sub-100 nm（双光子/纳米铸造） | Einck/Kim | C70/C66 · [310,253] |")
    A("")
    A("### 7.4 物理/手性纪录（对 BIC 项目最相关）")
    A("")
    A("| 指标 | 纪录 | 案例 | 出处 |")
    A("| --- | --- | --- | --- |")
    A("| 固有手性 BIC | **CD 0.93、Q>2663**（可见，倾斜扰动 TiO₂，斜刻蚀系统） | Chen 2023 | C67 · [84]（Nature 613, 474） |")
    A("| 双层手性 | CD 0.7（双层 Si，两步 EBL） | Tanaka 2020 | C57 · [303] |")
    A("| 结构色色域 | 181.8% sRGB / 135.6% Adobe RGB / 97.2% Rec.2020 | Yang 2020 | C01 · [28]（Sec.5.2） |")
    A("| VUV 非线性 | 197 nm 相干产生（ZnO，FIB） | Semmlinger 2018 | C11 · [168] |")
    A("")
    A("---")
    A("")
    A("## 8. 案例结构解读（哪些技术在“垄断”哪些故事）")
    A("")
    A(f"1. **标准光刻是创新引擎**（{grp['standard']}/{len(CASES)} 例）：EBL/FIB/LDW 案例最多，几乎所有“第一次”（首次手性 BIC、首次 3D 打印 metalens、首次 THz 石墨烯）都在这一层发生。它的代价是面积小、贵、慢——正文 Table 1 的“分辨率-速度-成本”三角。")
    A("2. **灰度/多步/SPL 是“维度扩展器”**：把制造从平面 X-Y 扩展到 Z（灰度控深度）与多层对准（多步），是“进阶技能”。")
    A(f"3. **大规模光刻是量产主线**（{grp['large-scale']}/{len(CASES)} 例）：DUV 是当前最成熟的答案（12 英寸、100 mm 先例），NIL 以“一步复制 + 90.6% 效率”提供低成本高保真路线，自组装以极低成本覆盖最大面积但自由度受限。")
    A(f"4. **极端制造负责破纪录**（{grp['extreme']}/{len(CASES)} 例）：多层/柔性/倾斜/高深宽比分别对应手性、共形、强偏振与大相位延迟需求；每条都以“工艺上的难”换“物理上的新”。")
    A("")
    A("---")
    A("")
    A("## 9. 对本项目（L01 / L02）的可迁移结论")
    A("")
    A("| 我们的问题 | F08 案例依据 | 行动建议 |")
    A("| --- | --- | --- |")
    A("| L01 单层 PMMA 路线表面质量上限？（报告 §5.6 路线矩阵） | TiO₂ ALD 反向填充粗糙度 **<1 nm**、侧壁近 90°（C04/C69）；GaN top-down EBL+etch 效率 91.6%（C06） | “胶/掩模决定几何”路线可行；用剂量测试片 + SEM 统计（Q1-11 流程）验收 σ |")
    A("| L01/F-01 dose-to-depth 调 Q 的机理归属 | 灰度光刻 = 变剂量 → 变孔深 → 变结构高度（C30–C33；EBL/UV/2PP/FIB 四路均有） | 若需纵向渐变 Q，灰度 EBL 是现成手段；与 F-01 “剂量控深”互证 |")
    A("| 高 Q 弱扰动态的加工容差压力（Q∝δ⁻²、σ∝Q⁻²） | 最干净几何纪录 <1 nm 粗糙度 / 89–90° 侧壁 / <60 nm CD 都可对标；SPL+deep RIE 87±2° | 工艺验收目标 σ≤2 nm（理想 1 nm）有文献先例支撑 |")
    A("| L01 未来若做强偏振椭率 χ / 手性 | 固有手性 BIC 靠“面内 α + 面外斜角 φ 联合破缺”：CD 0.93、Q>2663（C67） | 记录为“进阶选项”：工艺复杂度高（斜刻蚀系统），先不进入第一轮 |")
    A("| L02 金属相位库 / 效率对标 | Au/SiO₂/Au 属金属-介质混合类（C36 两步对准、C14/C15 FIB 3D 混合） | 对准误差需计入容差预算；单层结构免对准是 L01 的相对优势 |")
    A("| 远期量产路线选择 | KrF/ArF 12 英寸与 100 mm 玻璃（C41–C45）、NIL 一步 PER 90.6%（C49）、dewetting 20×11 cm²（C55） | 与既有结论一致：DUV 为量产答案、NIL 为绿色高保真备选 |")
    A("| 器件面积风险（L01 数十万–百万孔估算） | 写场拼接/邻近效应在正文未展开，但 12 英寸先例证明晶圆级可行 | 拼接/邻近效应问题在流片/DUV 路线内已被工业界解决，EBL 单写场内先验证 |")
    A("")
    A("> 注：F08 案例引用号与本库文献体系对照——[268] = 本库 **F-09**（Park 2019 all-glass metalens）；[101] 与 F-08 笔记中“1.5 μm TiO₂ 高深宽比消色差透镜”一致；[104] 倾斜 TiO₂ 光栅即笔记 §4.3 案例。")
    A("")
    A("---")
    A("")
    A("## 10. 附录：F08 案例全清单（72 例，可逐例复核）")
    A("")
    A("> 编号 C01–C72 与正文一一对应；出处列为 F08 参考文献号，图列为 F08 插图号。")
    A("")
    cur_grp = None
    for c in CASES:
        g = c["grp"]
        if g != cur_grp:
            A(f"### {GROUP_CN[g]}")
            A("")
            A("| 编号 | 工艺 | 作者(年) | 材料 | 器件/功能 | 波段 | 关键指标 | F08 出处 |")
            A("| --- | --- | --- | --- | --- | --- | --- | --- |")
            cur_grp = g
        A(f"| {c['id']} | {c['tech']} | {c['author']} | {c['mat']} | {c['func']} | {eff_band(c)} | {c['metric']} | {c['ref']} {c['fig']} |")
    A("")
    A("### 一句话提及（不计入统计）")
    A("")
    for m in MENTIONS:
        A(f"- {m}")
    A("")
    A("---")
    A("")
    A("> 生成方式：本报告由脚本从 F08 原文逐例提取数据后自动统计生成（数据文件 `f08_cases.py`），统计口径见 §2；如需增删案例或改分类，请同步修改数据后重新生成，避免手工改表造成口径不一致。")
    A("")

    txt = "\n".join(L)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(txt)
    print("written:", OUT, "lines:", len(L))
    print("total cases:", len(CASES))
    print("group:", dict(grp))
    print("tech family:", dict(tech_family))
    print("func:", dict(func), "sum:", sum(func.values()))
    print("bands:", dict(bands), "n_banded:", n_banded)
    print("matfreq:", dict(matfreq))

if __name__ == "__main__":
    main()
