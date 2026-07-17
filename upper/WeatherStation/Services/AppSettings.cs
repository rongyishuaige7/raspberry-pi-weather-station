using System;
using System.IO;
using System.Text.Json;

namespace WeatherStation.Services;

/// <summary>把少量用户偏好（服务器地址等）持久化到本地 JSON 文件，跨平台。</summary>
public static class AppSettings
{
    private static readonly string _filePath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "WeatherStation",
        "prefs.json");

    private sealed class Prefs
    {
        public string ApiBaseUrl { get; set; } = "http://127.0.0.1:5000";
    }

    private static Prefs _prefs = Load();

    private static Prefs Load()
    {
        try
        {
            if (File.Exists(_filePath))
            {
                var json = File.ReadAllText(_filePath);
                return JsonSerializer.Deserialize<Prefs>(json) ?? new Prefs();
            }
        }
        catch { /* 读取失败时使用默认值 */ }
        return new Prefs();
    }

    private static void Save()
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(_filePath)!);
            File.WriteAllText(_filePath, JsonSerializer.Serialize(_prefs,
                new JsonSerializerOptions { WriteIndented = true }));
        }
        catch { /* 写入失败静默忽略，不影响主功能 */ }
    }

    public static string ApiBaseUrl
    {
        get => _prefs.ApiBaseUrl;
        set
        {
            if (_prefs.ApiBaseUrl == value) return;
            _prefs.ApiBaseUrl = value;
            Save();
        }
    }
}
