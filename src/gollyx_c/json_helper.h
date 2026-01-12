#ifndef JSON_HELPER_H
#define JSON_HELPER_H

typedef enum {
    JSON_NULL,
    JSON_BOOL,
    JSON_NUMBER,
    JSON_STRING,
    JSON_ARRAY,
    JSON_OBJECT
} JsonType;

typedef struct JsonValue JsonValue;

struct JsonValue {
    JsonType type;
    union {
        int boolean;
        double number;
        char *string;
        struct {
            JsonValue **values;
            int count;
        } array;
        struct {
            char **keys;
            JsonValue **values;
            int count;
        } object;
    } data;
};

JsonValue* json_parse(const char *json);
void json_free(JsonValue *value);

JsonValue* json_get(JsonValue *obj, const char *key);
const char* json_as_string(JsonValue *val);
double json_as_number(JsonValue *val);
int json_as_int(JsonValue *val);
int json_as_bool(JsonValue *val);

#endif
