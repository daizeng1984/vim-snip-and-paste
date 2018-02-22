import neovim;
import os;
import re;
import subprocess;
import mimetypes;
import uuid;
import shutil;
import errno;

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

def save_clipboard_image_mac(output_folder, output_image_filename):
    basename, extname = os.path.splitext(output_image_filename);
    if not extname :
        print("no ext name found, will not apply");
        output_image_filename = "";
    matchimage = re.compile(r'(class\s+PNGf)|(class\s+PNG)|(class\s+8BPS)|(class\s+jp2)|(class\s+BMP)|(class\s+TPIC)', re.UNICODE);
    check = subprocess.Popen(("osascript", "-e", "clipboard info", "2&>1" ), stdout=subprocess.PIPE)
    res = check.stdout.read().decode("utf-8");
    matchimageext = re.compile(r'image/');
    if matchimage.search(res):
        if not output_image_filename:
            output_image_filename = create_random_filename();
        mkdir_p(output_folder);
        subprocess.Popen(("pngpaste", output_folder + "/" + output_image_filename));
        return (output_image_filename, "pngpaste this image as: " + output_folder + "/" + output_image_filename);
    else:
        pb = subprocess.Popen(("pbpaste"), stdout=subprocess.PIPE);
        image_file = pb.stdout.read().decode("utf-8");
        image_name = os.path.basename(image_file);
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
        image_name, desc = save_clipboard_image_mac(output_folder, "");
        self.vim.command('echo "' + desc + '"');
        if image_name:
            self.vim.command('normal i' + '![' + os.path.splitext(image_name)[0] + '](' + '.' + img_folder + '/' + image_name + ')');

