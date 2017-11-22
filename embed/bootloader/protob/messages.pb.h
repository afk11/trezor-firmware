/* Automatically generated nanopb header */
/* Generated by nanopb-0.4.0-dev */

#ifndef PB_MESSAGES_PB_H_INCLUDED
#define PB_MESSAGES_PB_H_INCLUDED
#include <pb.h>

#include "types.pb.h"

/* @@protoc_insertion_point(includes) */
#if PB_PROTO_HEADER_VERSION != 30
#error Regenerate this file with the current version of nanopb generator.
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Enum definitions */
typedef enum _MessageType {
    MessageType_MessageType_Initialize = 0,
    MessageType_MessageType_Ping = 1,
    MessageType_MessageType_Success = 2,
    MessageType_MessageType_Failure = 3,
    MessageType_MessageType_FirmwareErase = 6,
    MessageType_MessageType_FirmwareUpload = 7,
    MessageType_MessageType_FirmwareRequest = 8,
    MessageType_MessageType_Features = 17,
    MessageType_MessageType_ButtonRequest = 26,
    MessageType_MessageType_ButtonAck = 27,
    MessageType_MessageType_GetFeatures = 55
} MessageType;
#define _MessageType_MIN MessageType_MessageType_Initialize
#define _MessageType_MAX MessageType_MessageType_GetFeatures
#define _MessageType_ARRAYSIZE ((MessageType)(MessageType_MessageType_GetFeatures+1))

/* Struct definitions */
typedef struct _ButtonAck {
    char dummy_field;
/* @@protoc_insertion_point(struct:ButtonAck) */
} ButtonAck;

typedef struct _GetFeatures {
    char dummy_field;
/* @@protoc_insertion_point(struct:GetFeatures) */
} GetFeatures;

typedef struct _Initialize {
    char dummy_field;
/* @@protoc_insertion_point(struct:Initialize) */
} Initialize;

typedef struct _ButtonRequest {
    bool has_code;
    ButtonRequestType code;
    bool has_data;
    char data[256];
/* @@protoc_insertion_point(struct:ButtonRequest) */
} ButtonRequest;

typedef struct _Failure {
    bool has_code;
    FailureType code;
    bool has_message;
    char message[256];
/* @@protoc_insertion_point(struct:Failure) */
} Failure;

typedef PB_BYTES_ARRAY_T(20) Features_revision_t;
typedef PB_BYTES_ARRAY_T(32) Features_bootloader_hash_t;
typedef struct _Features {
    bool has_vendor;
    char vendor[33];
    bool has_major_version;
    uint32_t major_version;
    bool has_minor_version;
    uint32_t minor_version;
    bool has_patch_version;
    uint32_t patch_version;
    bool has_bootloader_mode;
    bool bootloader_mode;
    bool has_device_id;
    char device_id[25];
    bool has_pin_protection;
    bool pin_protection;
    bool has_passphrase_protection;
    bool passphrase_protection;
    bool has_language;
    char language[17];
    bool has_label;
    char label[33];
    bool has_initialized;
    bool initialized;
    bool has_revision;
    Features_revision_t revision;
    bool has_bootloader_hash;
    Features_bootloader_hash_t bootloader_hash;
    bool has_imported;
    bool imported;
    bool has_pin_cached;
    bool pin_cached;
    bool has_passphrase_cached;
    bool passphrase_cached;
    bool has_firmware_present;
    bool firmware_present;
/* @@protoc_insertion_point(struct:Features) */
} Features;

typedef struct _FirmwareErase {
    bool has_length;
    uint32_t length;
/* @@protoc_insertion_point(struct:FirmwareErase) */
} FirmwareErase;

typedef struct _FirmwareRequest {
    bool has_offset;
    uint32_t offset;
    bool has_length;
    uint32_t length;
/* @@protoc_insertion_point(struct:FirmwareRequest) */
} FirmwareRequest;

typedef PB_BYTES_ARRAY_T(32) FirmwareUpload_hash_t;
typedef struct _FirmwareUpload {
    pb_callback_t payload;
    bool has_hash;
    FirmwareUpload_hash_t hash;
/* @@protoc_insertion_point(struct:FirmwareUpload) */
} FirmwareUpload;

typedef struct _Ping {
    bool has_message;
    char message[256];
    bool has_button_protection;
    bool button_protection;
    bool has_pin_protection;
    bool pin_protection;
    bool has_passphrase_protection;
    bool passphrase_protection;
/* @@protoc_insertion_point(struct:Ping) */
} Ping;

typedef struct _Success {
    bool has_message;
    char message[256];
/* @@protoc_insertion_point(struct:Success) */
} Success;

/* Default values for struct fields */

/* Initializer values for message structs */
#define Initialize_init_default                  {0}
#define GetFeatures_init_default                 {0}
#define Features_init_default                    {false, "", false, 0, false, 0, false, 0, false, 0, false, "", false, 0, false, 0, false, "", false, "", false, 0, false, {0, {0}}, false, {0, {0}}, false, 0, false, 0, false, 0, false, 0}
#define Ping_init_default                        {false, "", false, 0, false, 0, false, 0}
#define Success_init_default                     {false, ""}
#define Failure_init_default                     {false, (FailureType)0, false, ""}
#define ButtonRequest_init_default               {false, (ButtonRequestType)0, false, ""}
#define ButtonAck_init_default                   {0}
#define FirmwareErase_init_default               {false, 0}
#define FirmwareRequest_init_default             {false, 0, false, 0}
#define FirmwareUpload_init_default              {{{NULL}, NULL}, false, {0, {0}}}
#define Initialize_init_zero                     {0}
#define GetFeatures_init_zero                    {0}
#define Features_init_zero                       {false, "", false, 0, false, 0, false, 0, false, 0, false, "", false, 0, false, 0, false, "", false, "", false, 0, false, {0, {0}}, false, {0, {0}}, false, 0, false, 0, false, 0, false, 0}
#define Ping_init_zero                           {false, "", false, 0, false, 0, false, 0}
#define Success_init_zero                        {false, ""}
#define Failure_init_zero                        {false, (FailureType)0, false, ""}
#define ButtonRequest_init_zero                  {false, (ButtonRequestType)0, false, ""}
#define ButtonAck_init_zero                      {0}
#define FirmwareErase_init_zero                  {false, 0}
#define FirmwareRequest_init_zero                {false, 0, false, 0}
#define FirmwareUpload_init_zero                 {{{NULL}, NULL}, false, {0, {0}}}

/* Field tags (for use in manual encoding/decoding) */
#define ButtonRequest_code_tag                   1
#define ButtonRequest_data_tag                   2
#define Failure_code_tag                         1
#define Failure_message_tag                      2
#define Features_vendor_tag                      1
#define Features_major_version_tag               2
#define Features_minor_version_tag               3
#define Features_patch_version_tag               4
#define Features_bootloader_mode_tag             5
#define Features_device_id_tag                   6
#define Features_pin_protection_tag              7
#define Features_passphrase_protection_tag       8
#define Features_language_tag                    9
#define Features_label_tag                       10
#define Features_initialized_tag                 12
#define Features_revision_tag                    13
#define Features_bootloader_hash_tag             14
#define Features_imported_tag                    15
#define Features_pin_cached_tag                  16
#define Features_passphrase_cached_tag           17
#define Features_firmware_present_tag            18
#define FirmwareErase_length_tag                 1
#define FirmwareRequest_offset_tag               1
#define FirmwareRequest_length_tag               2
#define FirmwareUpload_payload_tag               1
#define FirmwareUpload_hash_tag                  2
#define Ping_message_tag                         1
#define Ping_button_protection_tag               2
#define Ping_pin_protection_tag                  3
#define Ping_passphrase_protection_tag           4
#define Success_message_tag                      1

/* Struct field encoding specification for nanopb */
extern const pb_field_t Initialize_fields[1];
extern const pb_field_t GetFeatures_fields[1];
extern const pb_field_t Features_fields[18];
extern const pb_field_t Ping_fields[5];
extern const pb_field_t Success_fields[2];
extern const pb_field_t Failure_fields[3];
extern const pb_field_t ButtonRequest_fields[3];
extern const pb_field_t ButtonAck_fields[1];
extern const pb_field_t FirmwareErase_fields[2];
extern const pb_field_t FirmwareRequest_fields[3];
extern const pb_field_t FirmwareUpload_fields[3];

/* Maximum encoded size of messages (where known) */
#define Initialize_size                          0
#define GetFeatures_size                         0
#define Features_size                            209
#define Ping_size                                265
#define Success_size                             259
#define Failure_size                             270
#define ButtonRequest_size                       270
#define ButtonAck_size                           0
#define FirmwareErase_size                       6
#define FirmwareRequest_size                     12
/* FirmwareUpload_size depends on runtime parameters */

/* Message IDs (where set with "msgid" option) */
#ifdef PB_MSGID

#define MESSAGES_MESSAGES \


#endif

#ifdef __cplusplus
} /* extern "C" */
#endif
/* @@protoc_insertion_point(eof) */

#endif