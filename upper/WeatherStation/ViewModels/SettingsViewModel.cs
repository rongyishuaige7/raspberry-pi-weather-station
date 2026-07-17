using System.Collections.Generic;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class SettingsViewModel : ViewModelBase
{
    private readonly ApiService _api;

    [ObservableProperty] private string _tempHigh = "35";

    [ObservableProperty] private string _tempLow = "5";

    [ObservableProperty] private string _humidityHigh = "85";

    [ObservableProperty] private string _humidityLow = "20";

    [ObservableProperty] private string _lightHigh = "50000";

    [ObservableProperty] private string _lightLow = "0";

    [ObservableProperty] private string _collectInterval = "5";

    [ObservableProperty] private string _status = "";

    public SettingsViewModel(ApiService api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        Status = "加载中…";
        var env = await _api.GetAsync<Dictionary<string, string>>("/api/settings");
        if (env.Code != 200 || env.Data == null)
        {
            Status = env.Message ?? "加载失败";
            return;
        }

        var d = env.Data;
        if (d.TryGetValue("temp_high", out var v)) TempHigh = v;
        if (d.TryGetValue("temp_low", out v)) TempLow = v;
        if (d.TryGetValue("humidity_high", out v)) HumidityHigh = v;
        if (d.TryGetValue("humidity_low", out v)) HumidityLow = v;
        if (d.TryGetValue("light_high", out v)) LightHigh = v;
        if (d.TryGetValue("light_low", out v)) LightLow = v;
        if (d.TryGetValue("collect_interval", out v)) CollectInterval = v;
        Status = "已加载";
    }

    [RelayCommand]
    private async Task SaveAsync()
    {
        Status = "保存中…";
        var body = new Dictionary<string, string>
        {
            ["temp_high"] = TempHigh,
            ["temp_low"] = TempLow,
            ["humidity_high"] = HumidityHigh,
            ["humidity_low"] = HumidityLow,
            ["light_high"] = LightHigh,
            ["light_low"] = LightLow,
            ["collect_interval"] = CollectInterval,
        };
        var env = await _api.PostJsonAsync<object>("/api/settings", body);
        if (env.Code == 200)
        {
            // 保存成功后立即从服务端拉取最新值，确保上位机本地阈值与服务端一致
            await LoadAsync();
            Status = "已保存并同步";
        }
        else
        {
            Status = env.Message ?? "保存失败";
        }
    }
}
