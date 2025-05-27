# add_missing_drivers.ps1
$jsonPath = "C:\Users\Dsekr\TelegramBot\driver_parser\driver_data.json"

# Проверка существования файла
if (-not (Test-Path $jsonPath)) {
    Write-Host "Ошибка: Файл $jsonPath не найден"
    exit
}

# Проверка прав доступа
if (-not (Get-Acl $jsonPath | Select-Object -ExpandProperty Access | Where-Object { $_.IdentityReference -like "*$env:USERNAME*" -and $_.FileSystemRights -match "Write|FullControl" })) {
    Write-Host "Ошибка: Нет прав на запись в $jsonPath"
    exit
}

# Загрузка JSON
try {
    $jsonContent = Get-Content $jsonPath -Raw -ErrorAction Stop | ConvertFrom-Json
    Write-Host "JSON загружен, записей: $(($jsonContent.drivers | Measure-Object).Count)"
} catch {
    Write-Host "Ошибка загрузки JSON: $_"
    exit
}

# Проверка дубликатов ID
$duplicates = $jsonContent.drivers | Group-Object id | Where-Object { $_.Count -gt 1 }
if ($duplicates) {
    Write-Host "Найдены дубликаты ID: $($duplicates.Name)"
    exit
}

# Список всех ожидаемых ID
$allDriverIds = @(
    "driver_5", "driver_6", "driver_7", "driver_8", "driver_9", "driver_10",
    "driver_11", "driver_12", "driver_13", "driver_14", "driver_15", "driver_16",
    "driver_17", "driver_18", "driver_19", "driver_20", "driver_21", "driver_22",
    "driver_23", "driver_24_sokolova", "driver_25", "driver_26_kovaleva", "driver_27",
    "driver_28", "driver_29", "driver_30_kovaleva", "driver_31", "driver_32",
    "driver_33", "driver_34", "driver_35", "driver_36_vehicle_cleaning",
    "driver_37", "driver_38_kovaleva", "driver_39_morozova", "driver_40_smirnov_new",
    "driver_41_kuznetsov_new2", "driver_42_petrov_new2", "driver_43_ivanov_new2",
    "driver_44_sidorova_new", "driver_45_volodin_new2", "driver_46_kovalev_new",
    "driver_47_morozov_new", "driver_48_ivanova_new2", "driver_49_popov_new2",
    "driver_50_sidorova_new",
    "driver_51_placeholder", "driver_52_placeholder", "driver_53_placeholder",
    "driver_54_placeholder", "driver_55_placeholder", "driver_56_placeholder",
    "driver_57_placeholder", "driver_58_placeholder", "driver_59_placeholder",
    "driver_60_placeholder", "driver_61_placeholder", "driver_62_placeholder",
    "driver_63_placeholder", "driver_64_placeholder", "driver_65_placeholder",
    "driver_66_placeholder", "driver_67_placeholder", "driver_68_placeholder",
    "driver_69_placeholder", "driver_70_placeholder", "driver_71_placeholder",
    "driver_72_placeholder", "driver_73_placeholder", "driver_74_placeholder",
    "driver_75_placeholder", "driver_76_placeholder"
)

# Проверка недостающих ID
$existingDriverIds = $jsonContent.drivers.id
$missingDriverIds = $allDriverIds | Where-Object { $_ -notin $existingDriverIds }
Write-Host "Недостающие ID: $missingDriverIds"

$newDrivers = @()

# Определение новых водителей
switch ($true) {
    "driver_5" {
        $newDriver = @{
            id = "driver_5"
            variants = @(
                @{
                    input = "Driver: Ivanov Ivan Ivanovich\nPhone: 8 911 123 45 67\nPassport: 1234 567890 issued by UFMS Russia, Moscow 01.01.2020\nLicense: 1234 567890\nVehicle: Lada Vesta A123456 77\nTrailer: PR789012\nCarrier: IP Ivanov"
                    expected = @{
                        Driver = "Ivanov Ivan Ivanovich"
                        ПК_серия_и_номер = "1234 567890"
                        ПК_место_выдачи = "UFMS Russia, Moscow"
                        ПК_дата_выдачи = "01.01.2020"
                        ВУ_серия_и_номер = "1234 567890"
                        Телефон = @("+7 (911) 123-45-67")
                        Автомобиль = "Lada Vesta A123456 77"
                        Прицеп = "PR789012"
                        Перевозчик = "IP Ivanov"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                }
            )
        }
        $newDrivers += $newDriver
    }

    # Шаблонные блоки для driver_6–driver_29
    { $_ -in @("driver_6", "driver_7", "driver_8", "driver_9", "driver_10", "driver_11", "driver_12", "driver_13", "driver_14", "driver_15", "driver_16", "driver_17", "driver_18", "driver_19", "driver_20", "driver_21", "driver_22", "driver_23", "driver_24_sokolova", "driver_25", "driver_26_kovaleva", "driver_27", "driver_28", "driver_29") } {
        $newDriver = @{
            id = $_
            variants = @(
                @{
                    input = "Driver: Driver $_\nPhone: 8 900 000 00$($_.Replace('driver_', ''))\nPassport: 0000 0000$($_.Replace('driver_', ''))0 issued by UFMS Russia 01.01.2020\nLicense: 0000 0000$($_.Replace('driver_', ''))\nVehicle: Car $_\nTrailer: TR0000$($_.Replace('driver_', ''))\nCarrier: IP Carrier"
                    expected = @{
                        Driver = "Driver $_"
                        ПК_серия_и_номер = "0000 0000$($_.Replace('driver_', ''))0"
                        ПК_место_выдачи = "UFMS Russia"
                        ПК_дата_выдачи = "01.01.2020"
                        ВУ_серия_и_номер = "0000 0000$($_.Replace('driver_', ''))"
                        Телефон = @("+7 (900) 000-00-$($_.Replace('driver_', ''))")
                        Автомобиль = "Car $_"
                        Прицеп = "TR0000$($_.Replace('driver_', ''))"
                        Перевозчик = "IP Carrier"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                }
            )
        }
        $newDrivers += $newDriver
    }

    "driver_30_kovaleva" {
        $newDriver = @{
            id = "driver_30_kovaleva"
            variants = @(
                @{
                    input = "Driver: Kovaleva Svetlana Petrovna\nPhone: 8 927 234 56 78\nPassport: 6437 789456 issued by UFMS Russia, Arkhangelsk Region 10.10.2020\nLicense: 9947 789456\nVehicle: Volvo K890 UT 29\nTrailer: AN123456\nCarrier: IP Sokolov"
                    expected = @{
                        Driver = "Kovaleva Svetlana Petrovna"
                        ПК_серия_и_номер = "6437 789456"
                        ПК_место_выдачи = "UFMS Russia, Arkhangelsk Region"
                        ПК_дата_выдачи = "10.10.2020"
                        ВУ_серия_и_номер = "9947 789456"
                        Телефон = @("+7 (927) 234-56-78")
                        Автомобиль = "Volvo K890 UT 29"
                        Прицеп = "AN123456"
                        Перевозчик = "IP Sokolov"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                },
                @{
                    input = "Kovaleva S.P.\nPassport: 6437789456\nUFMS Arkhangelsk 10.10.20\nPhone: 89272345678\nVolvo K890 UT 29\nTrailer: AN123456\nCarrier: IP Sokolov"
                    expected = @{
                        Driver = "Kovaleva Svetlana Petrovna"
                        ПК_серия_и_номер = "6437 789456"
                        ПК_место_выдачи = "UFMS Arkhangelsk"
                        ПК_дата_выдачи = "10.10.2020"
                        ВУ_серия_и_номер = "9947 789456"
                        Телефон = @("+7 (927) 234-56-78")
                        Автомобиль = "Volvo K890 UT 29"
                        Прицеп = "AN123456"
                        Перевозчик = "IP Sokolov"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                }
            )
        }
        $newDrivers += $newDriver
    }

    # Шаблонные блоки для driver_31–driver_37 и driver_39–driver_50
    { $_ -in @("driver_31", "driver_32", "driver_33", "driver_34", "driver_35", "driver_36_vehicle_cleaning", "driver_37", "driver_39_morozova", "driver_40_smirnov_new", "driver_41_kuznetsov_new2", "driver_42_petrov_new2", "driver_43_ivanov_new2", "driver_44_sidorova_new", "driver_45_volodin_new2", "driver_46_kovalev_new", "driver_47_morozov_new", "driver_48_ivanova_new2", "driver_49_popov_new2", "driver_50_sidorova_new") } {
        $newDriver = @{
            id = $_
            variants = @(
                @{
                    input = "Driver: Driver $_\nPhone: 8 900 000 00$($_.Replace('driver_', ''))\nPassport: 0000 0000$($_.Replace('driver_', ''))0 issued by UFMS Russia 01.01.2020\nLicense: 0000 0000$($_.Replace('driver_', ''))\nVehicle: Car $_\nTrailer: TR0000$($_.Replace('driver_', ''))\nCarrier: IP Carrier"
                    expected = @{
                        Driver = "Driver $_"
                        ПК_серия_и_номер = "0000 0000$($_.Replace('driver_', ''))0"
                        ПК_место_выдачи = "UFMS Russia"
                        ПК_дата_выдачи = "01.01.2020"
                        ВУ_серия_и_номер = "0000 0000$($_.Replace('driver_', ''))"
                        Телефон = @("+7 (900) 000-00-$($_.Replace('driver_', ''))")
                        Автомобиль = "Car $_"
                        Прицеп = "TR0000$($_.Replace('driver_', ''))"
                        Перевозчик = "IP Carrier"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                }
            )
        }
        $newDrivers += $newDriver
    }

    "driver_38_kovaleva" {
        $newDriver = @{
            id = "driver_38_kovaleva"
            variants = @(
                @{
                    input = "Driver: Kovaleva Svetlana Petrovna\nPhone: 8 927 234 56 79\nPassport: 6438 789457 issued by UFMS Russia, Arkhangelsk 11.10.2020\nLicense: 9948 789457\nVehicle: Volvo K891 UT 29\nTrailer: AN123457\nCarrier: IP Sokolov"
                    expected = @{
                        Driver = "Kovaleva Svetlana Petrovna"
                        ПК_серия_и_номер = "6438 789457"
                        ПК_место_выдачи = "UFMS Russia, Arkhangelsk"
                        ПК_дата_выдачи = "11.10.2020"
                        ВУ_серия_и_номер = "9948 789457"
                        Телефон = @("+7 (927) 234-56-79")
                        Автомобиль = "Volvo K891 UT 29"
                        Прицеп = "AN123457"
                        Перевозчик = "IP Sokolov"
                        Дата_рождения = $null
                        Прописка = ""
                        Адрес_регистрации = $null
                    }
                }
            )
        }
        $newDrivers += $newDriver
    }

    "driver_51_placeholder" {
        $newDriver = @{
            id = "driver_51_placeholder"
            variants = @()
        }
        $newDrivers += $newDriver
    }

    # Заполнители driver_52_placeholder–driver_76_placeholder
    { $_ -in @("driver_52_placeholder", "driver_53_placeholder", "driver_54_placeholder", "driver_55_placeholder", "driver_56_placeholder", "driver_57_placeholder", "driver_58_placeholder", "driver_59_placeholder", "driver_60_placeholder", "driver_61_placeholder", "driver_62_placeholder", "driver_63_placeholder", "driver_64_placeholder", "driver_65_placeholder", "driver_66_placeholder", "driver_67_placeholder", "driver_68_placeholder", "driver_69_placeholder", "driver_70_placeholder", "driver_71_placeholder", "driver_72_placeholder", "driver_73_placeholder", "driver_74_placeholder", "driver_75_placeholder", "driver_76_placeholder") } {
        $newDriver = @{
            id = $_
            variants = @()
        }
        $newDrivers += $newDriver
    }
}

# Диагностика: сколько водителей подготовлено
Write-Host "Подготовлено водителей: $($newDrivers.Count)"

# Добавление новых записей
$addedCount = 0
foreach ($driverId in $missingDriverIds) {
    $newDriver = $newDrivers | Where-Object { $_.id -eq $driverId }
    if ($newDriver) {
        $jsonContent.drivers += $newDriver
        $addedCount++
    }
}

# Сохранение JSON
try {
    $jsonContent | ConvertTo-Json -Depth 10 -Compress | Set-Content $jsonPath -Encoding UTF8 -Force
    Write-Host "Добавлено новых записей: $addedCount"
    Write-Host "JSON сохранён: $jsonPath"
} catch {
    Write-Host "Ошибка сохранения JSON: $_"
    exit
}

# Проверка результата
try {
    $updatedJson = Get-Content $jsonPath -Raw -ErrorAction Stop | ConvertFrom-Json
    $updatedCount = ($updatedJson.drivers | Measure-Object).Count
    Write-Host "Записей в JSON: $updatedCount"
    $updatedJson.drivers | Select-Object id | Sort-Object id | ForEach-Object { Write-Host $_.id }
} catch {
    Write-Host "Ошибка проверки JSON: $_"
}