#include <jni.h>
#include "InfluxDBClient.h"

#include <iostream>
#include <string>
#include <curl/curl.h>
#include <nlohmann/json.hpp>
#include <fstream>

using namespace std;
using json = nlohmann::json;

// Loads all required variables from .env
string read_env(const string& var) {
    const char* value = getenv(var.c_str());
    if (value == nullptr) {
        cerr << "Environment variable " << var << " not set." << endl;
        exit(EXIT_FAILURE);
    }
    return string(value);
}

// Write html response to a buffer
size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    ((string*)userp)->append((char*)contents, size * nmemb);
    return size * nmemb;
}

// Main function to perform the Flux query
extern "C" {
    JNIEXPORT void JNICALL Java_InfluxDBClient_performFluxQuery(JNIEnv* env, jobject obj, jstring jFluxQuery) {
        const char* fluxQuery = env->GetStringUTFChars(jFluxQuery, 0);

        string token = read_env("INFLUXDB_TOKEN");
        string org = read_env("INFLUXDB_ORG");
        string bucket = read_env("INFLUXDB_BUCKET");
        string url = read_env("INFLUXDB_URL");

        CURL* curl;
        CURLcode res;
        string readBuffer;

        curl_global_init(CURL_GLOBAL_DEFAULT);
        curl = curl_easy_init();

        if (curl) {
            struct curl_slist* headers = nullptr;
            headers = curl_slist_append(headers, ("Authorization: Token " + token).c_str());
            headers = curl_slist_append(headers, "Content-Type: application/vnd.flux");

            curl_easy_setopt(curl, CURLOPT_URL, (url + "/api/v2/query?org=" + org).c_str());
            curl_easy_setopt(curl, CURLOPT_POSTFIELDS, fluxQuery);
            curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
            curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(curl, CURLOPT_WRITEDATA, &readBuffer);

            res = curl_easy_perform(curl);
            if (res != CURLE_OK) {
                fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
            } else {
                cout << readBuffer << endl;
            }

            curl_easy_cleanup(curl);
            curl_slist_free_all(headers);
        }

        curl_global_cleanup();
        env->ReleaseStringUTFChars(jFluxQuery, fluxQuery);
    }
}
