using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using WeatherStation.Models;
using WeatherStation.Services;

namespace WeatherStation.ViewModels;

public partial class AlarmViewModel : ViewModelBase
{
    private readonly ApiService _api;

    [ObservableProperty] private string _status = "";

    public ObservableCollection<AlarmRow> Rows { get; } = new();

    public AlarmViewModel(ApiService api)
    {
        _api = api;
    }

    [RelayCommand]
    private async Task LoadAsync()
    {
        Status = "加载中…";
        Rows.Clear();
        var env = await _api.GetAsync<AlarmRow[]>("/api/alarms?limit=500");
        if (env.Code != 200)
        {
            Status = env.Message ?? $"错误 {env.Code}";
            return;
        }

        var data = env.Data;
        if (data == null)
        {
            Status = "无数据";
            return;
        }

        foreach (var r in data)
            Rows.Add(r);
        Status = $"共 {Rows.Count} 条";
    }
}
