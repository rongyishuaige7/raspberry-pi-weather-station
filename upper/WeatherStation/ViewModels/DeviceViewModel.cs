using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using WeatherStation.Models;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class DeviceViewModel : ViewModelBase
{
    private readonly ApiService _api;

    [ObservableProperty] private string _deviceName = "";

    [ObservableProperty] private string _deviceNo = "";

    [ObservableProperty] private string _location = "";

    [ObservableProperty] private string _status = "";

    public ObservableCollection<DeviceRow> Rows { get; } = new();

    public DeviceViewModel(ApiService api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        Status = "加载中…";
        Rows.Clear();
        var env = await _api.GetAsync<DeviceRow[]>("/api/devices");
        if (env.Code != 200)
        {
            Status = env.Message ?? $"错误 {env.Code}";
            return;
        }

        if (env.Data == null)
        {
            Status = "无数据";
            return;
        }

        foreach (var r in env.Data)
            Rows.Add(r);
        Status = $"共 {Rows.Count} 台";
    }

    [RelayCommand]
    private async Task AddAsync()
    {
        if (string.IsNullOrWhiteSpace(DeviceName))
        {
            Status = "请填写设备名称";
            return;
        }

        var body = new System.Collections.Generic.Dictionary<string, object?>
        {
            ["device_name"] = DeviceName.Trim(),
            ["device_no"] = string.IsNullOrWhiteSpace(DeviceNo) ? null : DeviceNo.Trim(),
            ["location"] = string.IsNullOrWhiteSpace(Location) ? null : Location.Trim(),
        };
        var env = await _api.PostJsonAsync<object>("/api/devices", body);
        Status = env.Code == 200 ? "已添加" : env.Message ?? "失败";
        if (env.Code == 200)
            await LoadAsync();
    }
}
