"""
Folders and file types per folder.
The file types order does not matter here.
"""
CATEGORIES = (
    "archives"  ".tar .tar.gz .tgz .gz   .bzip .bz  .bzip2 .bz2 .zip    .zipx    .rar .7z .xz" " "
                ".lz  .lz4    .lzh .lzma .lzo  .lzx .ace   .msi .tar.bz .tar.bz2",

    "audio"     ".aa  .aac .ac3 .adx .ahx .wav .aiff .mp1 .mp2 .mp3  .mpc .ogg .ape" " "
                ".asf .au  .aud .dmf .dts .dxd .flac .mmf .mod .opus .ra  .tta     " " "
                ".voc .vox .vqf .wma .xm  .mqa .psf  .spc .ym  .vgm  .wav .amr",

    "video"     ".webm .mkv .flv .vob .ogv .drc .avi .mts .m2ts .ts          " " "
                ".mov .qt .wmv .rm .rmvb .viv .asf .amv .mp4 .m4p .m4v       " " "
                ".mpg .mp2 .mpeg .mpe .mpv .m2v .svi .3gp .3g2 .nsv .f4v .f4p" " "
                ".f4a .f4b",

    "pictures"  ".bmp .jpg .jpeg .gif .png .tiff .tif .svg .eps",

    "textbooks" ".pdf .epub .fb2 .htmlz .htxt",

    "docs"      ".doc .txt .docx .xls .xlsx .ppt .pptx .dot .odt",

    "work"      ".ai .cdr .yuv .glade .c  .cpp .cxx .py .vba .bas .pas .swi" " "
                ".po .pod .mo  .qxd   .pm .dat",

    "internet"  ".url .html .css",

    "trash"     ".tmp .torrent",
)

"""
First symbol is "bad", other symbols up to ',' is sample to substitute.
"""
FILENAME_TRANSLATION_TABLE = (
    " _,аa,бb,вv,гg,дd,еe,ёe,жsz,зz,иy,йj,кk,лl,мm,нn,оo,пp,рr,"
    "сs,тt,уu,фf,хh,цc,чch,шw,щsw,ъ,ыy,ь,эe,юyu,яya,єye,іi,їyi,ґg"
)
