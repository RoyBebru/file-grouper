# -*- coding: utf-8 -*-

import common
_ = common._ # for i18n

import os
import sys
import getopt
from pathlib import (Path, PurePath)
import shutil


def print_usage():
    script_name = Path(sys.argv[0]).name
    print(_("Usage format: ") + os.linesep +
            f"  1) {script_name} [-l] -d <DEST_ROOT_DIR> <INSPECTED_DIR>" + os.linesep +
            f"  2) {script_name} -t" + os.linesep +
            f"  3) {script_name} -h" + os.linesep +
            f"  4) {script_name}" + os.linesep +
            _("      Where <DEST_ROOT_DIR> under '-d'/'--dir' option is the directory to move") + os.linesep +
            _("  categorized files per created assigned subdirectories. The <INSPECTED_DIR>") + os.linesep +
            _("  directory must be inspected. Option '-t'/'--types' prints file types per category") + os.linesep +
            _("  subdirectory and exits. Option '-h'/'--help' prints this text. Option '-l'/'--links'") + os.linesep +
            _("  serves to making links instead of moving files. Option '-G'/'--no-gui' disable GUI mode.")
            )


def AreDirsAdequate():
    return Path(common.option_inspected_dir) not in Path(common.option_base_dir).parents


def IsWorkinWithinCommonDir():
    return Path(common.option_inspected_dir) == Path(common.option_base_dir)


def parse_options():
    """Parsing command line option"""
    def print_extension_list():
        is_not_first_iter = False
        for folder_name, ext_list in common.categories.items():
            if is_not_first_iter:
                print("")
            is_not_first_iter = True
            folder_field = folder_name
            extension_field = ""
            for ext in ext_list:
                if extension_field != "":
                    extension_field += ' '
                extension_field += ext
                if len(extension_field) > 55:
                    print("{:>10s}: {:s}".format(folder_field, extension_field))
                    extension_field = ""
                    folder_field = ""
            if extension_field != "":
                print("{:>10s}: {:s}".format(folder_field, extension_field))

    script_dir = str(Path(sys.argv[0]).parent.resolve())
    common.option_no_gui = False
    common.option_make_links = False
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv
                , "d:lthG"
                , ["links", "dir=", "types", "help", "nogui", "no-gui"])
    except getopt.GetoptError as err:
        print("*** Option error:", err, file=sys.stderr)
        quit()

    for (opt, arg) in opts:
        if opt in ("-d", "--dir"):
            pathdir = os.path.realpath(arg)
            if common.option_base_dir:
                print(_("*** Warning: only first option '-d' is applied"), file=sys.stderr)
            else:
                common.option_base_dir = pathdir
        elif opt in ("-t", "--types"):
            print_extension_list()
            quit(0)

        elif opt in ("-h", "--help"):
            print_usage()
            quit(0)

        elif opt in ("-G", "--nogui", "--no-gui"):
            common.option_no_gui = True

        elif opt in ("-l", "--links"):
            common.option_make_links = True

    if len(args) > 1:
        print(_("*** Error: must be only one inspected directory"), file=sys.stderr)
        quit(1)

    if len(args) != 0:
        pathdir = os.path.realpath(args[0])
        if not os.path.isdir(pathdir):
            print(_("*** Error: '%s' is not valid directory") % args[0], file=sys.stderr)
            quit(1)
        common.option_inspected_dir = pathdir

    if common.option_base_dir == "":
        common.option_base_dir = common.option_inspected_dir

    if common.option_base_dir != "" or common.option_base_dir != "":
        if not AreDirsAdequate():
            print(_("*** Error: -d directory ('%s') cannot be ") % common.option_base_dir
                  + _("(sub-)directory of the inspected directory ('%s')") % common.option_inspected_dir
                  , file=sys.stderr)
            quit(1)

    if script_dir == common.option_base_dir:
        print(_("*** Error: in option '-d' '%s' must be other than program directory")
              % common.option_base_dir, file=sys.stderr)
        quit(1)


def is_any_to_do():
    return bool(common.option_base_dir) and bool(common.option_inspected_dir)


def get_category_pathdirs():
    """Return list of Path category dirs if used the same dir"""
    if not IsWorkinWithinCommonDir:
        return []
    category_dirs = []
    path_base_dir = Path(common.option_base_dir)
    for category in common.categories.keys():
        category_dirs.append(path_base_dir / category)
    return category_dirs


def get_reverse_sorted_path_dirs(pathdir: str, alldirs=False):
    """Return PurePath'es objects for each subdirectory in directory"""
    path = Path(pathdir)
    if alldirs:
        category_dirs = []
    else:
        category_dirs = get_category_pathdirs()
    dirs = []
    for dir in path.glob("**/**"):
        if dir in category_dirs:
            continue
        for cdir in category_dirs:
            if cdir in dir.parents: # dir is subdir of cdir?
                break
        else:
            # Append dir if it is not subdir of categories dir
            dirs.append(dir)
    dirs.sort(reverse = True)
    return dirs


def get_path_files_from_path_dir(dir: Path):
    """Returns PurePath"""
    files = [f for f in dir.iterdir() if f.is_file()]
    return files


def find_category(filename: str):
    fnlower = filename.lower()
    for category, exts in common.categories.items():
        # exts is sorted: so, ".tar.gz" must be found before ".gz"
        for ext in exts:
            if fnlower.endswith(ext):
                return (category
                        , filename[:-len(ext)] # remove extension
                        , ext)
    return ("", filename, "")


def resolve_existent_filename_collision(category, name, ext):
    version = 0
    while True:
        if version == 0:
            path = PurePath(common.option_base_dir, category, name + ext)
        else:
            path = PurePath(common.option_base_dir
                            , category
                            , name + "_{:03d}".format(version) + ext)
        if not Path(path).exists():
            return path
        version += 1


def normilize(name):
    return name.translate(common.filename_translation_table)


def sanitize_filename(filename: str) -> str:
    """Return empty string if file does not match any category"""
    (category, name, ext) = find_category(filename)
    if category == "":
        return ("", "") # file is not match any category
    name = normilize(name)
    return (resolve_existent_filename_collision(category, name, ext), ext)


def action_per_ext(file, ext):
    if ext.lower() in [".zip", ".xz", ".bz", ".tar", ".tgz", ".gz", ".bz2"
                       , ".bzip", ".bzip2", ".tar.gz", ".tar.bz", ".tar.bz2"]:
        try:
            dir = str(file)
            dir = Path(dir[:-len(ext)])
            dir.mkdir(exist_ok = True)
            shutil.unpack_archive(str(file), str(dir))
        except:
            pass
            

def handle_one_path_file(file: Path):
    (purepath_filename, ext) = sanitize_filename(file.name)
    if not bool(purepath_filename):
        return # file is not match any category
    err = None
    while True:
        try:
            if common.option_make_links:
                if common.is_win:
                    file.link_to(purepath_filename)
                else:
                    link = Path(purepath_filename)
                    link.symlink_to(file)
            else:
                file.rename(purepath_filename)
            err = None
            action_per_ext(purepath_filename, ext)
            break
        except FileNotFoundError as e:
            dir = Path(purepath_filename.parent)
            # Create non existent folder
            dir.mkdir(parents=True, exist_ok=True)
            err = e.strerror
            continue
        except Exception as e:
            err = "error"
            break
    if bool(err):
        print(f"{file.name}: {err}", file=sys.stderr)


def do_everything():
    dirs = get_reverse_sorted_path_dirs(common.option_inspected_dir)
    category_dirs = get_category_pathdirs()
    for dir in dirs:
        if dir in category_dirs:
            # Do not handle files into the category dirs
            continue
        files = get_path_files_from_path_dir(dir)
        for file in files:
            handle_one_path_file(file)
    if not common.option_make_links:
        # Delete empty folders
        for dir in dirs:
            amount_items = 0
            for item in dir.iterdir():
                if item.is_file():
                    amount_items += 1
                elif item.is_dir() and not item.is_symlink():
                    amount_items += 1
            if amount_items == 0:
                shutil.rmtree(dir)
