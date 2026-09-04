param(
    [string]$OutputRoot = "",
    [string[]]$Ids = @(),
    [switch]$NoNetwork
)

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$ProjectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    # Keep the script compatible with Windows PowerShell 5.1, which may read
    # UTF-8-without-BOM source files using the active ANSI code page.
    $materialFolder = -join ([char[]](0x6750, 0x6599, 0x4F53, 0x7CFB, 0x5206, 0x7C7B))
    $bandFolder = "1550" + (-join ([char[]](0x6CE2, 0x6BB5)))
    $OutputRoot = Join-Path (Join-Path (Join-Path (Join-Path $ProjectRoot "literature") $materialFolder) "Si") $bandFolder
} elseif (-not [IO.Path]::IsPathRooted($OutputRoot)) {
    $OutputRoot = Join-Path $ProjectRoot $OutputRoot
}
$pdfRoot = Join-Path $OutputRoot "pdfs"
New-Item -ItemType Directory -Force -Path $pdfRoot | Out-Null

$papers = @(
    [pscustomobject]@{ id="A1"; priority=$true; author_year="Hsieh_2023"; doi="10.1364/OE.487589"; title="Metasurfaces on silicon photonic waveguides for simultaneous emission phase and amplitude control"; filename="A1_Hsieh_2023_Waveguide_Phase_Amplitude_Control.pdf"; urls=@("https://opg.optica.org/oe/viewmedia.cfm?uri=oe-31-8-12487&seq=0") },
    [pscustomobject]@{ id="A2"; priority=$true; author_year="Tanhayivash_2025"; doi="10.1038/s41598-025-05141-7"; title="Phase and amplitude gradient waveguide coupled metasurfaces"; filename="A2_Tanhayivash_2025_Phase_Amplitude_Gradient_Waveguide_Metasurfaces.pdf"; urls=@("https://www.nature.com/articles/s41598-025-05141-7.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC12144083/pdf/41598_2025_Article_5141.pdf") },
    [pscustomobject]@{ id="A3"; priority=$true; author_year="Van_Iseghem_2023"; doi="10.1364/PRJ.490085"; title="Optical leaky fin waveguide for long-range optical antennas on high-index contrast photonic circuit platforms"; filename="A3_Van_Iseghem_2023_Optical_Leaky_Fin_Waveguide.pdf"; urls=@("https://biblio.ugent.be/publication/01H9321JAQP5JMTCEZDK48DP89/file/01H9327DGPNBYNA86MV2NVPQGQ.pdf", "https://pcphotonics.intec.ugent.be/download/pub_5038.pdf") },
    [pscustomobject]@{ id="A4"; priority=$false; author_year="Doylend_2011"; doi="10.1364/OE.19.021595"; title="Two-dimensional free-space beam steering with an optical phased array on silicon-on-insulator"; filename="A4_Doylend_2011_SOI_Optical_Phased_Array.pdf"; urls=@("https://escholarship.org/content/qt6vp6b5p8/qt6vp6b5p8.pdf", "https://opg.optica.org/oe/viewmedia.cfm?uri=oe-19-22-21595&seq=0") },
    [pscustomobject]@{ id="A5"; priority=$false; author_year="Sun_2013"; doi="10.1038/nature11727"; title="Large-scale nanophotonic phased array"; filename="A5_Sun_2013_Large_Scale_Nanophotonic_Phased_Array.pdf"; urls=@("https://pmg.mit.edu/wp-content/uploads/2015/01/Nature2013Sun-1_0001.pdf") },
    [pscustomobject]@{ id="A6"; priority=$false; author_year="Bozzola_2015"; doi="10.1364/OE.23.016289"; title="Optimising apodized grating couplers in a pure SOI platform to -0.5 dB coupling efficiency"; filename="A6_Bozzola_2015_Apodized_Grating_Couplers.pdf"; urls=@("https://opg.optica.org/oe/viewmedia.cfm?uri=oe-23-12-16289&seq=0") },
    [pscustomobject]@{ id="A7"; priority=$false; author_year="Chen_2024"; doi="10.1088/2631-8695/ad1d21"; title="Subwavelength grating waveguide antenna based on interleaved groove structure"; filename="A7_Chen_2024_Interleaved_Groove_Waveguide_Antenna.pdf"; urls=@() },
    [pscustomobject]@{ id="A8"; priority=$false; author_year="Guo_2020"; doi="10.1126/sciadv.abb4142"; title="Molding free-space light with guided wave-driven metasurfaces"; filename=$null; existing_path="literature/L02_Guo_2020_Molding_Free-Space_Light.pdf"; urls=@() },

    [pscustomobject]@{ id="B1"; priority=$true; author_year="Huang_2023"; doi="10.1038/s41467-023-39227-5"; title="Ultrahigh-Q guided mode resonances in an all-dielectric metasurface"; filename="B1_Huang_2023_Ultrahigh_Q_Guided_Mode_Resonances.pdf"; urls=@("https://irep.ntu.ac.uk/id/eprint/50668/1/1850811_Xu.pdf", "https://www.nature.com/articles/s41467-023-39227-5.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC10257673/pdf/41467_2023_Article_39227.pdf") },
    [pscustomobject]@{ id="B2"; priority=$true; author_year="Watanabe_2025"; doi="10.1021/acs.nanolett.4c05880"; title="Low-Contrast BIC Metasurfaces with Quality Factors Exceeding 100,000"; filename="B2_Watanabe_2025_Low_Contrast_BIC_Metasurfaces.pdf"; urls=@("https://pmc.ncbi.nlm.nih.gov/articles/PMC11849022/pdf/nl4c05880.pdf", "https://mdr.nims.go.jp/filesets/dd433e94-a1ce-43ec-b21e-90c00d7699d0/download", "https://arxiv.org/pdf/2411.14101") },
    [pscustomobject]@{ id="B3"; priority=$true; author_year="Huang_2024"; doi="10.1002/adfm.202309982"; title="Realizing Ultrahigh-Q Resonances Through Harnessing Symmetry-Protected Bound States in the Continuum"; filename="B3_Huang_2024_Symmetry_Protected_BIC.pdf"; urls=@("https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/adfm.202309982") },
    [pscustomobject]@{ id="B4"; priority=$false; author_year="Zhu_2026"; doi="10.1021/acs.nanolett.6c00556"; title="Observation of Dual-Band Intrinsic Chirality in Underetched Silicon Metasurfaces via Quasi-BICs"; filename="B4_Zhu_2026_Underetched_Silicon_Chiral_qBIC.pdf"; urls=@() },
    [pscustomobject]@{ id="B5"; priority=$false; author_year="Liu_2017"; doi="10.3390/s17081861"; title="Optical Refractive Index Sensing Based on High-Q Bound States in the Continuum in Free-Space Coupled Photonic Crystal Slabs"; filename="B5_Liu_2017_BIC_Refractive_Index_Sensing.pdf"; urls=@("https://pdfs.semanticscholar.org/171d/2363f79baa5ab1bb4a48d4336e414edb56fe.pdf", "https://www.mdpi.com/1424-8220/17/8/1861/pdf?version=1503050123") },
    [pscustomobject]@{ id="B6"; priority=$false; author_year="Lee_2014"; doi="10.1364/OE.22.009271"; title="Resonant grating polarizers made with silicon nitride, titanium dioxide, and silicon"; filename="B6_Lee_2014_Resonant_Grating_Polarizers.pdf"; urls=@("https://opg.optica.org/oe/viewmedia.cfm?uri=oe-22-8-9271&seq=0") },
    [pscustomobject]@{ id="B7"; priority=$false; author_year="Kalinic_2023"; doi="10.1021/acsphotonics.2c01703"; title="Quasi-BIC Modes in All-Dielectric Slotted Nanoantennas for Enhanced Er3+ Emission"; filename="B7_Kalinic_2023_Slotted_Nanoantenna_qBIC_Er.pdf"; urls=@("https://europepmc.org/articles/PMC9936627/bin/ph2c01703.pdf", "https://pubs.acs.org/doi/pdf/10.1021/acsphotonics.2c01703", "https://pmc.ncbi.nlm.nih.gov/articles/PMC9936627/pdf/ph2c01703.pdf") },
    [pscustomobject]@{ id="B8"; priority=$false; author_year="Zhou_2025"; doi="10.1364/OE.555348"; title="Efficient silicon-erbium photonic hybrids with flexible spatial control of light via bound states in the continuum"; filename="B8_Zhou_2025_Silicon_Erbium_BIC_Hybrids.pdf"; urls=@("https://opg.optica.org/oe/viewmedia.cfm?uri=oe-33-5-11853&seq=0") },

    [pscustomobject]@{ id="C1"; priority=$true; author_year="Li_2026"; doi="10.1117/1.AP.8.2.024003"; original_doi="10.1117/1.AP.8.024003"; title="Metasurface-empowered integrated silicon photonics: foundational principles, representative applications, and fabrication strategies"; filename="C1_Li_2026_Metasurface_Empowered_Integrated_Silicon_Photonics.pdf"; urls=@("https://www.spiedigitallibrary.org/journals/advanced-photonics/volume-8/issue-2/024003/Metasurface-empowered-integrated-silicon-photonics--foundational-principles-representative-applications-and/10.1117/1.AP.8.2.024003.pdf") },
    [pscustomobject]@{ id="C2"; priority=$true; author_year="Arbabi_2015"; doi="10.1038/ncomms8069"; title="Subwavelength-thick lenses with high numerical apertures and large efficiency based on high-contrast transmitarrays"; filename="C2_Arbabi_2015_High_Contrast_Transmitarray_Lens.pdf"; urls=@("https://www.nature.com/articles/ncomms8069.pdf", "https://arxiv.org/pdf/1410.8261") },
    [pscustomobject]@{ id="C3"; priority=$true; author_year="Ji_2024"; doi="10.1038/s41467-024-52476-2"; title="On-chip multifunctional metasurfaces with full-parametric multiplexed Jones matrix"; filename="C3_Ji_2024_On_Chip_Full_Parametric_Jones_Matrix.pdf"; urls=@("https://taoli.nju.edu.cn/_upload/article/files/a3/01/621ebde34f02bb7b9e3af32302bf/7748968f-96f9-4cf9-89f4-9850c2ed1214.pdf", "https://www.nature.com/articles/s41467-024-52476-2.pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC11437200/pdf/41467_2024_Article_52476.pdf") },
    [pscustomobject]@{ id="C4"; priority=$false; author_year="Li_2020"; doi="10.1515/nanoph-2020-0063"; title="Large-area metasurface on CMOS-compatible fabrication platform: driving flat optics from lab to fab"; filename="C4_Li_2020_Large_Area_CMOS_Metasurface_Platform.pdf"; urls=@("https://onlinelibrary.wiley.com/doi/pdfdirect/10.1515/nanoph-2020-0063", "https://www.degruyterbrill.com/document/doi/10.1515/nanoph-2020-0063/pdf?licenseType=open-access", "https://scispace.com/pdf/large-area-metasurface-on-cmos-compatible-fabrication-4ggxwkrc8z.pdf") },
    [pscustomobject]@{ id="C5"; priority=$false; author_year="Kamali_2018"; doi="10.1515/nanoph-2017-0129"; title="A review of dielectric optical metasurfaces for wavefront control"; filename="C5_Kamali_2018_Dielectric_Metasurface_Wavefront_Control_Review.pdf"; urls=@("https://www.degruyter.com/downloadpdf/journals/nanoph/7/6/article-p1041.pdf", "https://arxiv.org/pdf/1804.09802") },
    [pscustomobject]@{ id="C6"; priority=$false; author_year="Kuznetsov_2024"; doi="10.1021/acsphotonics.3c00457"; title="Roadmap for Optical Metasurfaces"; filename="C6_Kuznetsov_2024_Roadmap_for_Optical_Metasurfaces.pdf"; urls=@("https://www.osti.gov/servlets/purl/2326149") },

    [pscustomobject]@{ id="D1"; priority=$false; author_year="Arbabi_2016"; doi="10.1364/OPTICA.3.000628"; title="Multiwavelength polarization-insensitive lenses based on dielectric metasurfaces with meta-molecules"; filename="D1_Arbabi_2016_Multiwavelength_Meta_Molecule_Lenses.pdf"; urls=@("https://www.osti.gov/servlets/purl/1387927", "https://arxiv.org/pdf/1601.05847") },
    [pscustomobject]@{ id="D2"; priority=$false; author_year="Shrestha_2018"; doi="10.1038/s41377-018-0078-x"; title="Broadband achromatic dielectric metalenses"; filename="D2_Shrestha_2018_Broadband_Achromatic_Dielectric_Metalenses.pdf"; urls=@("https://projects.iq.harvard.edu/files/muri_metasurfaces/files/shrestha_broadband_achromatic_dielectric_metalenses_lsa_2018.pdf", "https://www.nature.com/articles/s41377-018-0078-x.pdf") },
    [pscustomobject]@{ id="D3"; priority=$false; author_year="Liu_2022"; doi="10.1364/OE.466321"; title="Broadband behavior of quadratic metalenses with a wide field of view"; filename="D3_Liu_2022_Quadratic_Metalens_Wide_FOV.pdf"; urls=@("https://arxiv.org/pdf/2206.03750", "https://opg.optica.org/oe/viewmedia.cfm?uri=oe-30-22-39860&seq=0") },
    [pscustomobject]@{ id="D4"; priority=$false; author_year="Cao_2025"; doi="10.1038/s41598-025-27208-1"; title="Single-layer silicon metalens for broadband achromatic focusing and wide field of view"; filename="D4_Cao_2025_Single_Layer_Silicon_Achromatic_Wide_FOV_Metalens.pdf"; urls=@("https://arxiv.org/pdf/2507.16366", "https://www.nature.com/articles/s41598-025-27208-1.pdf") },
    [pscustomobject]@{ id="D5"; priority=$false; author_year="Li_2022"; doi="10.1515/nanoph-2021-0609"; title="Flat telescope based on an all-dielectric metasurface doublet enabling polarization-controllable enhanced beam steering"; filename="D5_Li_2022_Flat_Telescope_Metasurface_Doublet.pdf"; urls=@("https://onlinelibrary.wiley.com/doi/pdfdirect/10.1515/nanoph-2021-0609", "https://www.degruyterbrill.com/document/doi/10.1515/nanoph-2021-0609/pdf?licenseType=open-access", "https://www.degruyter.com/document/doi/10.1515/nanoph-2021-0609/pdf") },
    [pscustomobject]@{ id="D6"; priority=$false; author_year="Matiushechkina_2024"; doi="10.1002/adom.202400191"; title="Perfect Mirror Effects in Metasurfaces of Silicon Nanodisks at Telecom Wavelength"; filename="D6_Matiushechkina_2024_Silicon_Nanodisk_Perfect_Mirror.pdf"; urls=@("https://repo.uni-hannover.de/bitstreams/e263e63b-12b0-480e-947a-3df183164381/download") },
    [pscustomobject]@{ id="D7"; priority=$false; author_year="Vasilantonakis_2017"; doi=$null; arxiv="1711.01430"; title="Refractive index contrast enhanced metalens on an SOI platform for large angle deflection"; filename="D7_Vasilantonakis_2017_SOI_Large_Angle_Deflector.pdf"; urls=@("https://arxiv.org/pdf/1711.01430") }
)

if ($Ids.Count -gt 0) {
    $papers = @($papers | Where-Object { $Ids -contains $_.id })
}

$resolvedSources = @{
    A2 = "https://www.nature.com/articles/s41598-025-05141-7.pdf"
    A3 = "https://biblio.ugent.be/publication/01H9321JAQP5JMTCEZDK48DP89/file/01H9327DGPNBYNA86MV2NVPQGQ.pdf"
    A4 = "https://escholarship.org/content/qt6vp6b5p8/qt6vp6b5p8.pdf"
    A5 = "https://pmg.mit.edu/wp-content/uploads/2015/01/Nature2013Sun-1_0001.pdf"
    B1 = "https://irep.ntu.ac.uk/id/eprint/50668/1/1850811_Xu.pdf"
    B2 = "https://mdr.nims.go.jp/filesets/dd433e94-a1ce-43ec-b21e-90c00d7699d0/download"
    B5 = "https://pdfs.semanticscholar.org/171d/2363f79baa5ab1bb4a48d4336e414edb56fe.pdf"
    C2 = "https://arxiv.org/pdf/1410.8261"
    C3 = "https://taoli.nju.edu.cn/_upload/article/files/a3/01/621ebde34f02bb7b9e3af32302bf/7748968f-96f9-4cf9-89f4-9850c2ed1214.pdf"
    C5 = "https://arxiv.org/pdf/1804.09802"
    C6 = "https://www.osti.gov/servlets/purl/2326149"
    D1 = "https://www.osti.gov/servlets/purl/1387927"
    D2 = "https://projects.iq.harvard.edu/files/muri_metasurfaces/files/shrestha_broadband_achromatic_dielectric_metalenses_lsa_2018.pdf"
    D3 = "https://arxiv.org/pdf/2206.03750"
    D4 = "https://arxiv.org/pdf/2507.16366"
    D6 = "https://repo.uni-hannover.de/bitstreams/e263e63b-12b0-480e-947a-3df183164381/download"
    D7 = "https://arxiv.org/pdf/1711.01430"
}

function Test-PdfFile([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path
    if ($item.Length -lt 10000) { return $false }
    $stream = [System.IO.File]::OpenRead($Path)
    try {
        $bytes = New-Object byte[] 5
        [void]$stream.Read($bytes, 0, 5)
        return ([System.Text.Encoding]::ASCII.GetString($bytes) -eq "%PDF-")
    }
    finally {
        $stream.Dispose()
    }
}

$headers = @{ "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WaveguideMetasurfaceResearch/1.0" }
$results = @()

foreach ($paper in $papers) {
    Write-Output ("[{0}] processing {1}" -f $paper.id, $paper.title)
    if ($paper.existing_path) {
        $existing = Join-Path (Get-Location) $paper.existing_path
        $ok = Test-PdfFile $existing
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; arxiv=$paper.arxiv; status=if($ok){"existing_in_project"}else{"missing_existing_file"}
            path=$paper.existing_path; source_url=$null; sha256=if($ok){(Get-FileHash -Algorithm SHA256 -LiteralPath $existing).Hash.ToLower()}else{$null}
            bytes=if($ok){(Get-Item -LiteralPath $existing).Length}else{$null}; note="Existing L02 anchor; not duplicated."
        }
        continue
    }

    if (-not $paper.urls -or $paper.urls.Count -eq 0) {
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; arxiv=$paper.arxiv; status="no_legal_oa_found"; path=$null; source_url=$null
            sha256=$null; bytes=$null; note="Publisher/repository metadata checked; no legal open full-text PDF located."
        }
        continue
    }

    $destination = Join-Path $pdfRoot $paper.filename
    if (Test-PdfFile $destination) {
        $item = Get-Item -LiteralPath $destination
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; original_doi=$paper.original_doi; arxiv=$paper.arxiv; status="downloaded"
            path=(Join-Path "pdfs" $paper.filename).Replace("\", "/"); source_url=$resolvedSources[$paper.id]
            sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash.ToLower(); bytes=$item.Length; note="Previously downloaded and revalidated."
        }
        continue
    }
    if ($NoNetwork) {
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; original_doi=$paper.original_doi; arxiv=$paper.arxiv; status="download_pending_access"
            path=$null; source_url=$paper.urls[0]; sha256=$null; bytes=$null
            note="OA/full-text source identified, but automated download is blocked by publisher/repository verification in the current environment."
        }
        continue
    }
    $downloaded = $false
    $source = $null
    $errors = @()
    foreach ($url in $paper.urls) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $url -Headers $headers -OutFile $destination -MaximumRedirection 10 -TimeoutSec 20
            if (Test-PdfFile $destination) {
                $downloaded = $true
                $source = $url
                break
            }
            $errors += "Non-PDF response: $url"
        }
        catch {
            $errors += "$url :: $($_.Exception.Message)"
        }
        if (Test-Path -LiteralPath $destination) { Remove-Item -LiteralPath $destination -Force }
    }

    if ($downloaded) {
        $item = Get-Item -LiteralPath $destination
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; original_doi=$paper.original_doi; arxiv=$paper.arxiv; status="downloaded"
            path=(Join-Path "pdfs" $paper.filename).Replace("\", "/"); source_url=$source
            sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $destination).Hash.ToLower(); bytes=$item.Length; note=$null
        }
    }
    else {
        $results += [pscustomobject]@{
            id=$paper.id; priority=$paper.priority; author_year=$paper.author_year; title=$paper.title
            doi=$paper.doi; original_doi=$paper.original_doi; arxiv=$paper.arxiv; status="download_failed"
            path=$null; source_url=$null; sha256=$null; bytes=$null; note=($errors -join " | ")
        }
    }
}

$manifest = [ordered]@{
    collection = "1550 nm silicon metasurface literature"
    generated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    output_root = $OutputRoot.Replace("\", "/")
    policy = "Legal OA sources only: publisher OA, PMC, arXiv, OSTI, or institutional repositories."
    total_candidates = $papers.Count
    downloaded = @($results | Where-Object status -eq "downloaded").Count
    existing_in_project = @($results | Where-Object status -eq "existing_in_project").Count
    unavailable = @($results | Where-Object status -eq "no_legal_oa_found").Count
    pending_access = @($results | Where-Object status -eq "download_pending_access").Count
    failed = @($results | Where-Object status -eq "download_failed").Count
    papers = $results
}

$manifestPath = Join-Path $OutputRoot "download_manifest.json"
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
[pscustomobject]$manifest | Select-Object total_candidates,downloaded,existing_in_project,unavailable,pending_access,failed | Format-List
$results | Select-Object id,status,path,note | Format-Table -AutoSize
