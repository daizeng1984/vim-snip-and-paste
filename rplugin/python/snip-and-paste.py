import neovim;
import os;
import re;
import subprocess;
import mimetypes;
import uuid;
import shutil;
import errno;
from sys import platform

def create_random_filename():
    return 'img-' + str(uuid.uuid4()) + '.png';

# stolen from https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python#answer-600612
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# TODO: Consider use pygobj on mac and window?
if platform == "linux" or platform == "linux2":
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    def check_clipboard_image_and_type_linux():
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        image = clipboard.wait_for_image()
        return image is not None

    def extract_file_name_from_clipboard_linux():
        text = clipboard.wait_for_text()
        if text is not None:
            image_file = text
            image_name = os.path.basename(image_file);
        return (image_file, image_name)

    def save_clipbpard_image_linux(path):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        image = clipboard.wait_for_image()
        if image is not None:
            image.savev(path, 'png', [], [])
    

elif platform == "darwin":
    def check_clipboard_image_and_type_mac():
        matchimage = re.compile(r'(class\s+PNGf)|(class\s+PNG)|(class\s+8BPS)|(class\s+jp2)|(class\s+BMP)|(class\s+TPIC)', re.UNICODE);
        check = subprocess.Popen(("osascript", "-e", "clipboard info", "2&>1" ), stdout=subprocess.PIPE)
        res = check.stdout.read().decode("utf-8");
        return matchimage.search(res) is not None
        
    def extract_file_name_from_clipboard_mac():
        pb = subprocess.Popen(("pbpaste"), stdout=subprocess.PIPE);
        image_file = pb.stdout.read().decode("utf-8");
        image_name = os.path.basename(image_file);
        return (image_file, image_name)
        
    def save_clipbpard_image_mac(path):
        subprocess.Popen(("pngpaste", path));
elif platform == "win32":
    pass

    


def save_clipboard_image(output_folder, output_image_filename, check_clipboard_image_and_type, save_clipbpard_image, extract_file_name_from_clipboard):
    basename, extname = os.path.splitext(output_image_filename);
    if not extname :
        print("no ext name found, will not apply");
        output_image_filename = "";
    clipboard_has_image = check_clipboard_image_and_type()
    matchimageext = re.compile(r'image/');
    if clipboard_has_image:
        if not output_image_filename:
            output_image_filename = create_random_filename();
        mkdir_p(output_folder)
        clip_file_abspath = output_folder + "/" + output_image_filename
        save_clipbpard_image(clip_file_abspath)
        return (output_image_filename, "save this image from clipboard as: " + clip_file_abspath);
    else:
        image_file, image_name = extract_file_name_from_clipboard()
        if image_name:
            output_image_filename = image_name;
        typename = mimetypes.guess_type(image_file)[0];
        if typename and matchimageext.search(typename):
            if not output_image_filename:
                output_image_filename = create_random_filename();
            mkdir_p(output_folder);
            shutil.copyfile(image_file, output_folder + "/" + output_image_filename);
            return (output_image_filename, ("find image " + image_name + " and move it to " + output_folder));
        else:
            return (None, "not image file");


@neovim.plugin
class Main(object):
    def __init__(self, vim):
        self.vim = vim

    @neovim.command('SnipPaste', nargs='*')
    def SnipPaste(self, args):
        # TODO: wrapper to annotation
        apath = self.vim.eval('expand("%:p")');
        afolder = os.path.dirname(apath);
        img_folder = '/.snip-img.' + (os.path.basename(apath)) + '/';
        output_folder = afolder + img_folder;
        if platform == "linux" or platform == "linux2":
            image_name, desc = save_clipboard_image(output_folder, "", check_clipboard_image_and_type_linux, save_clipbpard_image_linux, extract_file_name_from_clipboard_linux);
        elif platform == "darwin":
            image_name, desc = save_clipboard_image(output_folder, "", check_clipboard_image_and_type_mac, save_clipbpard_image_mac, extract_file_name_from_clipboard_mac);
        elif platform == "win32":
            image_name, desc = (None, "We don't support windows at this point!")
        
        self.vim.command('echo "' + desc + '"');
        if image_name:
            self.vim.command('normal i' + '![' + os.path.splitext(image_name)[0] + '](' + '.' + img_folder + '/' + image_name + ')');

