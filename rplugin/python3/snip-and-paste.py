import neovim
import os
import re
import subprocess
import mimetypes
import uuid
import shutil
import errno
import importlib
from sys import platform


# create randome filename
def create_random_filename():
    return 'img-' + str(uuid.uuid4()) + '.png'


# stolen from
# https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python#answer-600612
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


gifound = importlib.util.find_spec("gi")

if (platform == "linux"
        or platform == "linux2"
        or platform == "windows"
        or (platform == 'darwin' and gifound)):
    if not gifound:
        raise Exception("Please install gi for python3 correctly!")
    import gi
    gi.require_version('Gtk', '3.0')

    def check_clipboard_image_and_type():
        from gi.repository import Gtk, Gdk
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        image = clipboard.wait_for_image()
        return image is not None

    def extract_file_name_from_clipboard():
        from gi.repository import Gtk, Gdk
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        text = clipboard.wait_for_text()
        if text is not None:
            image_file = text
            image_name = os.path.basename(image_file)
        return (image_file, image_name)

    def save_clipbpard_image(path):
        from gi.repository import Gtk, Gdk
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        image = clipboard.wait_for_image()
        if image is not None:
            image.savev(path, 'png', [], [])
elif platform == "darwin":
    # Nasty hack to use mac's clis and pngpaste
    def check_clipboard_image_and_type():
        matchimage = re.compile(
            r'(class\s+PNGf)|(class\s+PNG)|(class\s+8BPS)\
            |(class\s+jp2)|(class\s+BMP)|(class\s+TPIC)',
            re.UNICODE)
        check = subprocess.Popen(
            ("osascript", "-e", "clipboard info", "2&>1"),
            stdout=subprocess.PIPE)
        res = check.stdout.read().decode("utf-8")
        return matchimage.search(res) is not None

    def extract_file_name_from_clipboard():
        pb = subprocess.Popen(("pbpaste"), stdout=subprocess.PIPE)
        image_file = pb.stdout.read().decode("utf-8")
        image_name = os.path.basename(image_file)
        return (image_file, image_name)

    def save_clipbpard_image(path):
        if shutil.which("pngpaste") is None:
            raise Exception("Cannot find pngpaste, please brew install")
        subprocess.Popen(("pngpaste", path))

else:
    raise Exception("Platform unknown!")


def save_clipboard_image(output_folder, output_image_filename):
    if (platform == "linux" or platform == "linux2"
            or platform == "darwin" or platform == "windows"):
        basename, extname = os.path.splitext(output_image_filename)
        if not extname:
            print("no ext name found, will not apply")
            output_image_filename = ""
        clipboard_has_image = check_clipboard_image_and_type()
        matchimageext = re.compile(r'image/')
        if clipboard_has_image:
            if not output_image_filename:
                output_image_filename = create_random_filename()
            mkdir_p(output_folder)
            clip_file_abspath = output_folder + "/" + output_image_filename
            save_clipbpard_image(clip_file_abspath)
            return (output_image_filename,
                    "save this image from clipboard as: " + clip_file_abspath)
        else:
            image_file, image_name = extract_file_name_from_clipboard()
            if image_name:
                output_image_filename = image_name
            typename = mimetypes.guess_type(image_file)[0]
            if typename and matchimageext.search(typename):
                if not output_image_filename:
                    output_image_filename = create_random_filename()
                mkdir_p(output_folder)
                shutil.copyfile(image_file,
                                output_folder + "/" + output_image_filename)
                return (output_image_filename,
                        ("find image " + image_name +
                         " and move it to " + output_folder))
            else:
                return (None, "not image file")
    else:
        return (None, "We don't support this platform at this point!")


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim

    @neovim.command('SnipPaste', nargs='*')
    def SnipPaste(self, args):
        # TODO: wrapper to annotation
        apath = self.vim.eval('expand("%:p")')
        afolder = os.path.dirname(apath)
        img_folder = '/.snip-img.' + (os.path.basename(apath)) + '/'
        output_folder = afolder + img_folder
        image_name, desc = save_clipboard_image(output_folder, "")
        self.vim.command('echo "' + desc + '"')
        if image_name:
            self.vim.command('normal i' + '![' +
                             os.path.splitext(image_name)[0] +
                             '](' + '.' + img_folder + '/' + image_name + ')')

