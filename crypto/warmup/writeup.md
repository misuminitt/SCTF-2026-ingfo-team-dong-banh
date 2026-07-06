# Warmup — Writeup

**Category    :** Crypto  
**Difficulty  :** Medium  
**Description :**

}eheh_lanoisan_arauj_kusam_asib_atik_agomes_ti_kcerw_tuki_gnay_ay_tagnames_wtb_his_ag_ulud_pu_mraw{62FTCS


## Solve

Dari awal kita sudah tau Kalau diperhatikan, bagian akhirnya adalah

```text
{62FTCS
```

Bagian ini jika dibalik akan menjadi

```text
SCTF26{
```

Karena format flag SCTF diawali dengan `SCTF26{...}`, maka bisa disimpulkan bahwa teks tersebut adalah flag yang dibalik seluruhnya

Jadi cara menyelesaikannya cukup dengan membuat script sederhana untuk membalik string tersebut

```python
enc = "}eheh_lanoisan_arauj_kusam_asib_atik_agomes_ti_kcerw_tuki_gnay_ay_tagnames_wtb_his_ag_ulud_pu_mraw{62FTCS"

flag = enc[::-1]

print(flag)
```

ouput

```python
SCTF26{warm_up_dulu_ga_sih_btw_semangat_ya_yang_ikut_wreck_it_semoga_kita_bisa_masuk_juara_nasional_hehe}
```

## Flag

```text
SCTF26{warm_up_dulu_ga_sih_btw_semangat_ya_yang_ikut_wreck_it_semoga_kita_bisa_masuk_juara_nasional_hehe}
```