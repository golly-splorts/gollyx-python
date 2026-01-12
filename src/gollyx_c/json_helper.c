#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include "json_helper.h"

static const char *parse_value(const char *ptr, JsonValue **out);

static const char *skip_whitespace(const char *ptr) {
    while (*ptr && isspace((unsigned char)*ptr)) ptr++;
    return ptr;
}

static const char *parse_string(const char *ptr, char **out) {
    ptr++; // skip quote
    const char *start = ptr;
    int len = 0;
    while (*ptr && *ptr != '"') {
        if (*ptr == '\\') {
            ptr++;
            if (!*ptr) break; 
        }
        ptr++;
        len++;
    }
    // Allocate buffer (len is upper bound)
    char *res = malloc(len + 1);
    const char *p = start;
    char *d = res;
    // Reset ptr to start to re-traverse
    const char *scan = start;
    
    while (scan < ptr) {
        if (*scan == '\\') {
            scan++;
            if (*scan == '"') *d++ = '"';
            else if (*scan == '\\') *d++ = '\\';
            else if (*scan == '/') *d++ = '/';
            else if (*scan == 'b') *d++ = '\b';
            else if (*scan == 'f') *d++ = '\f';
            else if (*scan == 'n') *d++ = '\n';
            else if (*scan == 'r') *d++ = '\r';
            else if (*scan == 't') *d++ = '\t';
            else *d++ = *scan; // ignore others for now
        } else {
            *d++ = *scan;
        }
        scan++;
    }
    *d = 0;
    *out = res;
    if (*ptr == '"') ptr++;
    return ptr;
}

static const char *parse_number(const char *ptr, double *out) {
    char *end;
    *out = strtod(ptr, &end);
    return end;
}

static const char *parse_array(const char *ptr, JsonValue **out) {
    ptr++; // skip [
    JsonValue *arr = calloc(1, sizeof(JsonValue));
    arr->type = JSON_ARRAY;
    
    ptr = skip_whitespace(ptr);
    if (*ptr == ']') {
        *out = arr;
        return ptr + 1;
    }

    int capacity = 4;
    arr->data.array.values = malloc(capacity * sizeof(JsonValue*));
    
    while (*ptr) {
        JsonValue *val;
        ptr = parse_value(ptr, &val);
        if (arr->data.array.count == capacity) {
            capacity *= 2;
            arr->data.array.values = realloc(arr->data.array.values, capacity * sizeof(JsonValue*));
        }
        arr->data.array.values[arr->data.array.count++] = val;
        
        ptr = skip_whitespace(ptr);
        if (*ptr == ']') {
            *out = arr;
            return ptr + 1;
        }
        if (*ptr == ',') ptr++;
        ptr = skip_whitespace(ptr);
    }
    return ptr;
}

static const char *parse_object(const char *ptr, JsonValue **out) {
    ptr++; // skip {
    JsonValue *obj = calloc(1, sizeof(JsonValue));
    obj->type = JSON_OBJECT;
    
    ptr = skip_whitespace(ptr);
    if (*ptr == '}') {
        *out = obj;
        return ptr + 1;
    }

    int capacity = 4;
    obj->data.object.keys = malloc(capacity * sizeof(char*));
    obj->data.object.values = malloc(capacity * sizeof(JsonValue*));
    
    while (*ptr) {
        char *key;
        ptr = skip_whitespace(ptr);
        if (*ptr != '"') {
            // Error or unquoted key (not standard but possible)
            // assuming standard json
            break; 
        }
        ptr = parse_string(ptr, &key);
        
        ptr = skip_whitespace(ptr);
        if (*ptr == ':') ptr++;
        
        JsonValue *val;
        ptr = parse_value(ptr, &val);
        
        if (obj->data.object.count == capacity) {
            capacity *= 2;
            obj->data.object.keys = realloc(obj->data.object.keys, capacity * sizeof(char*));
            obj->data.object.values = realloc(obj->data.object.values, capacity * sizeof(JsonValue*));
        }
        obj->data.object.keys[obj->data.object.count] = key;
        obj->data.object.values[obj->data.object.count] = val;
        obj->data.object.count++;

        ptr = skip_whitespace(ptr);
        if (*ptr == '}') {
            *out = obj;
            return ptr + 1;
        }
        if (*ptr == ',') ptr++;
        ptr = skip_whitespace(ptr);
    }
    return ptr;
}

static const char *parse_value(const char *ptr, JsonValue **out) {
    ptr = skip_whitespace(ptr);
    if (!*ptr) return ptr;

    if (*ptr == '"') {
        char *s;
        ptr = parse_string(ptr, &s);
        *out = calloc(1, sizeof(JsonValue));
        (*out)->type = JSON_STRING;
        (*out)->data.string = s;
    } else if (*ptr == '[') {
        ptr = parse_array(ptr, out);
    } else if (*ptr == '{') {
        ptr = parse_object(ptr, out);
    } else if (strncmp(ptr, "true", 4) == 0) {
        *out = calloc(1, sizeof(JsonValue));
        (*out)->type = JSON_BOOL;
        (*out)->data.boolean = 1;
        ptr += 4;
    } else if (strncmp(ptr, "false", 5) == 0) {
        *out = calloc(1, sizeof(JsonValue));
        (*out)->type = JSON_BOOL;
        (*out)->data.boolean = 0;
        ptr += 5;
    } else if (strncmp(ptr, "null", 4) == 0) {
        *out = calloc(1, sizeof(JsonValue));
        (*out)->type = JSON_NULL;
        ptr += 4;
    } else {
        double d;
        ptr = parse_number(ptr, &d);
        *out = calloc(1, sizeof(JsonValue));
        (*out)->type = JSON_NUMBER;
        (*out)->data.number = d;
    }
    return ptr;
}

JsonValue* json_parse(const char *json) {
    JsonValue *val = NULL;
    parse_value(json, &val);
    return val;
}

void json_free(JsonValue *value) {
    if (!value) return;
    if (value->type == JSON_STRING) {
        free(value->data.string);
    } else if (value->type == JSON_ARRAY) {
        for (int i = 0; i < value->data.array.count; i++) {
            json_free(value->data.array.values[i]);
        }
        free(value->data.array.values);
    } else if (value->type == JSON_OBJECT) {
        for (int i = 0; i < value->data.object.count; i++) {
            free(value->data.object.keys[i]);
            json_free(value->data.object.values[i]);
        }
        free(value->data.object.keys);
        free(value->data.object.values);
    }
    free(value);
}

JsonValue* json_get(JsonValue *obj, const char *key) {
    if (!obj || obj->type != JSON_OBJECT) return NULL;
    for (int i = 0; i < obj->data.object.count; i++) {
        if (strcmp(obj->data.object.keys[i], key) == 0) {
            return obj->data.object.values[i];
        }
    }
    return NULL;
}

const char* json_as_string(JsonValue *val) {
    if (val && val->type == JSON_STRING) return val->data.string;
    return NULL;
}

double json_as_number(JsonValue *val) {
    if (val && val->type == JSON_NUMBER) return val->data.number;
    return 0.0;
}

int json_as_int(JsonValue *val) {
    return (int)json_as_number(val);
}

int json_as_bool(JsonValue *val) {
    if (val && val->type == JSON_BOOL) return val->data.boolean;
    return 0;
}
