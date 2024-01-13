#if 0  // self-compiling code: chmod +x this file and run it like a script
gcc -Wall -Werror keyboard-events.c -o keyboard-events && ./keyboard-events
exit 0
#endif

// This is modified example from https://www.kernel.org/doc/html/v4.12/input/uinput.html

#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <linux/uinput.h>

void emit(int fd, int type, int code, int val)
{
   struct input_event ie;

   ie.type = type;
   ie.code = code;
   ie.value = val;
   /* timestamp values below are ignored */
   ie.time.tv_sec = 0;
   ie.time.tv_usec = 0;

   write(fd, &ie, sizeof(ie));
}

void sendkey(int fd, int code) {
   emit(fd, EV_KEY, code, 1);
   emit(fd, EV_SYN, SYN_REPORT, 0);
   emit(fd, EV_KEY, code, 0);
   emit(fd, EV_SYN, SYN_REPORT, 0);
}

void sendkeyshift(int fd, int code) {
   emit(fd, EV_KEY, KEY_LEFTSHIFT, 1);
   emit(fd, EV_SYN, SYN_REPORT, 0);

   emit(fd, EV_KEY, code, 1);
   emit(fd, EV_SYN, SYN_REPORT, 0);
   emit(fd, EV_KEY, code, 0);
   emit(fd, EV_SYN, SYN_REPORT, 0);
   
   emit(fd, EV_KEY, KEY_LEFTSHIFT, 0);
   emit(fd, EV_SYN, SYN_REPORT, 0);
}

int main(void)
{
   struct uinput_setup usetup;

   int fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);


   /*
    * The ioctls below will enable the device that is about to be
    * created, to pass key events, in this case the space key.
    */
   ioctl(fd, UI_SET_EVBIT, EV_KEY);
   ioctl(fd, UI_SET_KEYBIT, KEY_SPACE);
   ioctl(fd, UI_SET_KEYBIT, KEY_H);
   ioctl(fd, UI_SET_KEYBIT, KEY_E);
   ioctl(fd, UI_SET_KEYBIT, KEY_L);
   ioctl(fd, UI_SET_KEYBIT, KEY_O);
   ioctl(fd, UI_SET_KEYBIT, KEY_1);
   ioctl(fd, UI_SET_KEYBIT, KEY_LEFTSHIFT);

   memset(&usetup, 0, sizeof(usetup));
   usetup.id.bustype = BUS_USB;
   usetup.id.vendor = 0x1234; /* sample vendor */
   usetup.id.product = 0x5678; /* sample product */
   strcpy(usetup.name, "Example device");

   ioctl(fd, UI_DEV_SETUP, &usetup);
   ioctl(fd, UI_DEV_CREATE);

   /*
    * On UI_DEV_CREATE the kernel will create the device node for this
    * device. We are inserting a pause here so that userspace has time
    * to detect, initialize the new device, and can start listening to
    * the event, otherwise it will not notice the event we are about
    * to send. This pause is only needed in our example code!
    */
   sleep(1);

   /* Key press, report the event, send key release, and report again */
   /*emit(fd, EV_KEY, KEY_SPACE, 1);
   emit(fd, EV_SYN, SYN_REPORT, 0);
   emit(fd, EV_KEY, KEY_SPACE, 0);
   emit(fd, EV_SYN, SYN_REPORT, 0);*/
   sendkey(fd, KEY_H);
   sendkey(fd, KEY_E);
   sendkey(fd, KEY_L);
   sendkey(fd, KEY_L);
   sendkey(fd, KEY_O);
   sendkeyshift(fd, KEY_1);
   sendkey(fd, KEY_SPACE);
   sendkeyshift(fd, KEY_H);
   sendkeyshift(fd, KEY_E);
   sendkeyshift(fd, KEY_L);
   sendkeyshift(fd, KEY_L);
   sendkeyshift(fd, KEY_O);
   sendkey(fd, KEY_SPACE);

   /*
    * Give userspace some time to read the events before we destroy the
    * device with UI_DEV_DESTOY.
    */
   sleep(1);

   ioctl(fd, UI_DEV_DESTROY);
   close(fd);

   return 0;
}
