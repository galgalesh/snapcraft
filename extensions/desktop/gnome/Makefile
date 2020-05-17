#!/usr/bin/make -f

SRC_DIR ?= .

PLATFORM_DIR := $(DESTDIR)/gnome-platform
DATA_DIR     := $(DESTDIR)/data-dir
BIN_DIR      := $(DESTDIR)/snap/command-chain
LIB_DIR	     := $(DESTDIR)/lib
DEST_LAUNCHER	:= desktop-launch
BINDTEXTDOMAIN	:= bindtextdomain.so
HW_PLATFORM     := $(shell uname --hardware-platform)
ARCH            := $(HW_PLATFORM)-linux-gnu
ifeq ($(HW_PLATFORM), x86_64)
ARCH_32     := i386-linux-gnu
endif

build: $(DEST_LAUNCHER)

clean:
	rm -f $(DEST_LAUNCHER)
	rm -f $(FLAVOR_FILE)
	rm -f $(BINDTEXTDOMAIN)

$(DEST_LAUNCHER):
	@cat $(SRC_DIR)/init >> $(DEST_LAUNCHER)
    # tail -n +2 to remove the shebang
	@tail -n +2 $(SRC_DIR)/desktop-exports >> $(DEST_LAUNCHER)
	@tail -n +2 $(SRC_DIR)/launcher-specific >> $(DEST_LAUNCHER)
	@tail -n +2 $(SRC_DIR)/mark-and-exec >> $(DEST_LAUNCHER)
	mkdir -p $(ARCH)
	gcc -Wall -O2 -o $(ARCH)/$(BINDTEXTDOMAIN) -fPIC -shared $(SRC_DIR)/../src/bindtextdomain.c -ldl
ifeq ($(HW_PLATFORM), x86_64)
	mkdir -p $(ARCH_32)
	gcc -m32 -Wall -O2 -o $(ARCH_32)/$(BINDTEXTDOMAIN) -fPIC -shared $(SRC_DIR)/../src/bindtextdomain.c -ldl
endif

install: $(DEST_LAUNCHER)
	install -d $(PLATFORM_DIR)
	install -d $(DATA_DIR)
	install -d $(DATA_DIR)/icons
	install -d $(DATA_DIR)/sounds
	install -d $(DATA_DIR)/themes
	install -D -m755 $(DEST_LAUNCHER) "$(BIN_DIR)"/$(DEST_LAUNCHER)
	install -D -m644 $(ARCH)/$(BINDTEXTDOMAIN) "$(LIB_DIR)"/$(ARCH)/$(BINDTEXTDOMAIN)
ifeq ($(HW_PLATFORM), x86_64)
	install -D -m644 $(ARCH_32)/$(BINDTEXTDOMAIN) "$(LIB_DIR)"/$(ARCH_32)/$(BINDTEXTDOMAIN)
endif
