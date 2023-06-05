
import re

import pymem
import ctypes

signature = b'{"context":{"description":"My Vibe","id":"user:onyourwave","type":"radio"},"tracks":[{"trackId":"'


def read_process_memory(process_name):
    result = b''

    try:
        pm = pymem.Pymem(process_name)

        print(pm.read_string())

        process_handle = ctypes.windll.kernel32.OpenProcess(
            ctypes.c_uint(0x1F0FFF), False, pm.process_id)

        if process_handle:
            base_address = ctypes.c_void_p(pm.process_base.lpBaseOfDll)
            buffer_size = 4096  # Размер буфера чтения, можно изменить по необходимости

            while True:
                buffer = ctypes.create_string_buffer(buffer_size)
                bytes_read = ctypes.c_ulong(0)

                ctypes.windll.kernel32.ReadProcessMemory(
                    process_handle, base_address, buffer, buffer_size, ctypes.byref(bytes_read))
                
                if bytes_read.value < buffer_size:
                    break

                result += buffer.raw

                base_address = ctypes.cast(
                    base_address.value + bytes_read.value, ctypes.c_void_p)

            ctypes.windll.kernel32.CloseHandle(process_handle)

            return result

    except pymem.exception.ProcessNotFound:
        pass

    return None


def find_signature_in_process_memory(process_memory, signature):

    match = re.search(re.escape(signature), process_memory)
    if match:
        offset = match.end()
        remaining_memory = process_memory[offset:]

        id_match = re.search(rb'/(\d+)/', remaining_memory)
        if id_match:
            id = id_match.group(1).decode('utf-8')
            return id
        else:
            return None
    else:
        return None


import ctypes.wintypes as wintypes

# Определение констант и структур для работы с операционной системой Windows
PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_VM_READ = 0x10
PAGE_READWRITE = 0x04

class PROCESS_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("hProcess", ctypes.c_void_p),
        ("hThread", ctypes.c_void_p),
        ("dwProcessId", ctypes.c_ulong),
        ("dwThreadId", ctypes.c_ulong)
    ]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong)
    ]

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [
        ('dwSize', wintypes.DWORD),
        ('cntUsage', wintypes.DWORD),
        ('th32ProcessID', wintypes.DWORD),
        ('th32DefaultHeapID', wintypes.ULONG),
        ('th32ModuleID', wintypes.DWORD),
        ('cntThreads', wintypes.DWORD),
        ('th32ParentProcessID', wintypes.DWORD),
        ('pcPriClassBase', wintypes.LONG),
        ('dwFlags', wintypes.DWORD),
        ('szExeFile', wintypes.CHAR * 260)
    ]

# Получение идентификатора процесса Y.Music.exe
process_name = "Y.Music.exe"
process_id = None
hProcess = None

import psutil

for proc in psutil.process_iter():
    if proc.name() == "Y.Music.exe":
        process_id = proc.pid

# Если найден идентификатор процесса, получаем доступ к его оперативной памяти
print(process_id)
if process_id:
    hProcess = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS | PROCESS_VM_READ, False, process_id)
    if hProcess:
        # Чтение содержимого оперативной памяти
        buffer_size = 4096
        buffer = ctypes.create_string_buffer(buffer_size)
        bytesRead = ctypes.c_ulong(0)
        while True:
            # Получение информации о следующем блоке памяти
            mbi = MEMORY_BASIC_INFORMATION()
            result = ctypes.windll.kernel32.VirtualQueryEx(hProcess, buffer, ctypes.byref(mbi), ctypes.sizeof(mbi))
            if result == 0:
                break

            # Проверка наличия доступных прав доступа
            if mbi.State == 0x1000 and mbi.Protect == PAGE_READWRITE:
                # Чтение содержимого памяти
                ctypes.windll.kernel32.ReadProcessMemory(hProcess, mbi.BaseAddress, buffer, buffer_size, ctypes.byref(bytesRead))
                
                # Обработка прочитанных данных, например, вывод на экран
                print(buffer.raw[:bytesRead.value])

            # Переход к следующему блоку памяти
            buffer = ctypes.create_string_buffer(buffer_size, base_address=mbi.BaseAddress + mbi.RegionSize)

        ctypes.windll.kernel32.CloseHandle(hProcess)
