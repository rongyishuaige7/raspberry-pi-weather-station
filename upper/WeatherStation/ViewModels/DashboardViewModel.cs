using System;
using System.Threading.Tasks;
using Avalonia.Threading;
using CommunityToolkit.Mvvm.ComponentModel;
using WeatherStation.Models;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class DashboardViewModel : ViewModelBase
{
    private readonly ApiService _api;
    private readonly SettingsViewModel _settings;
    private DispatcherTimer? _timer;

    [ObservableProperty] private double? _temperature;

    [ObservableProperty] private double? _humidity;

    [ObservableProperty] private double? _lightIntensity;

    [ObservableProperty] private string _lastUpdate = "—";

    [ObservableProperty] private string _statusText = "未连接";

    [ObservableProperty] private string _alarmHint = "";

    public DashboardViewModel(ApiService api, SettingsViewModel settings)
    {
        _api = api;
        _settings = settings;
    }

    public void StartPolling()
    {
        StopPolling();
        _timer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(2) };
        _timer.Tick += async (_, _) => await RefreshAsync();
        _timer.Start();
        _ = RefreshAsync();
    }

    public void StopPolling()
    {
        _timer?.Stop();
        _timer = null;
    }

    private async Task RefreshAsync()
    {
        try
        {
            var env = await _api.GetAsync<SensorDataRow>("/api/realtime");
            if (env.Code != 200)
            {
                StatusText = env.Message ?? $"错误 {env.Code}";
                return;
            }

            var row = env.Data;
            if (row == null)
            {
                StatusText = "暂无数据";
                AlarmHint = "";
                return;
            }

            Temperature = row.Temperature;
            Humidity = row.Humidity;
            LightIntensity = row.LightIntensity;
            LastUpdate = row.RecordedAt ?? "—";
            StatusText = "已收到最近一条记录";
            AlarmHint = CheckLocalAlarm(row, _settings);
        }
        catch (Exception ex)
        {
            StatusText = ex.Message;
        }
    }

    private static string CheckLocalAlarm(SensorDataRow row, SettingsViewModel s)
    {
        // TryParse 失败时返回 0，用 bool 标记是否解析成功，避免以 0 作为阈值误判
        bool tlOk = double.TryParse(s.TempLow,      System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var tl);
        bool thOk = double.TryParse(s.TempHigh,     System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var th);
        bool hlOk = double.TryParse(s.HumidityLow,  System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var hl);
        bool hhOk = double.TryParse(s.HumidityHigh, System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var hh);
        bool llOk = double.TryParse(s.LightLow,     System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var ll);
        bool lhOk = double.TryParse(s.LightHigh,    System.Globalization.NumberStyles.Any,
                        System.Globalization.CultureInfo.InvariantCulture, out var lh);

        // 阈值必须 high > low 才是有效配置，否则跳过该项判断
        var hints = new System.Collections.Generic.List<string>();

        if (tlOk && thOk && th > tl && row.Temperature.HasValue)
        {
            if (row.Temperature < tl || row.Temperature > th)
                hints.Add($"温度异常({row.Temperature:F1}℃)");
        }

        if (hlOk && hhOk && hh > hl && row.Humidity.HasValue)
        {
            if (row.Humidity < hl || row.Humidity > hh)
                hints.Add($"湿度异常({row.Humidity:F1}%)");
        }

        if (llOk && lhOk && lh > ll && row.LightIntensity.HasValue)
        {
            if (row.LightIntensity < ll || row.LightIntensity > lh)
                hints.Add($"光照异常({row.LightIntensity:F0}lux)");
        }

        return hints.Count == 0 ? "" : string.Join("  ", hints);
    }
}
