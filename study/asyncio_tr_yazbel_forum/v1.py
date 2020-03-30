# -------------------*Coroutine ve Task*-------------------------------------------------------------------
# Konu ile ilgili örnekler Python 3.7 içindir.
'''
Python coroutine:Asenkron olarak çalışan fonksiyonlara verilen addır.async def fonksiyon_adi():
şeklinde tanımlanırlar.await fonksiyon_adi() şeklinde çağırılırlar.
'''
# Coroutine Örneği
import asyncio  # asenkron için modül
import time


async def main():
    print("Merhaba")
    await asyncio.sleep(1)
    print("dünya")
    '''
    asyncio.sleep(1) bu metod asenkron olarak programı uyutur(bekletir) yani await asyncio.sleep(1)
    kodu yerine time modülü içindeki time.sleep(1) metodunu kullansaydık program bu satırda hiçbir işlev
    yapmadan bir saniye boyunca tüm programı bekletirdi yani tüm program bloke olurdu ancak 
    asyncio içindeki uyku metodunu kullanarak şunu diyoruz bu satıra gelince bir saniye bekle ama 
    ana programı bloke etme; şu aşamada bu uyku konusunun etkisi  time.sleep(1) ve asyncio.sleep(1) 
    aynı görünse de ilerleyen örneklerde farkı anlayabileceğiz.Şimdilik asenkronun programı bloklamadığını
    bilmemiz yeterli.
    await bu anahtar kelime ise şu işe yarar.Tüm coroutine fonksiyonlar (async ile tanımlanmış fonsiyon)
    diğer fonksiyonlar tarafından await anahtar kelimesi kullanılarak çağırılır.Görev tamamlanana kadar
    ana programı bloklamadan, bu await ile çağırılan fonksiyonun işlevini yerine getirmesini bekler.
    '''


# asyncio.run(main())  # run metodu ile de ana fonksiyon çalıştırılır.
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# asenkron fonksiyonlar diğer fonksiyonlar içinde şöyle çağırılır
import asyncio
import time


async def say_after(gecikme, konu):  # bu fonksiyon bir coroutine'dir ve çağırılırken await ile çağırılır
    await asyncio.sleep(gecikme)
    print(konu)


async def main():
    print(f"started at {time.strftime('%X')}")
    await say_after(1, 'hello')  # await ile çağırılır, zorunlu
    await say_after(2, 'world')  # await ile çağırılır, zorunlu
    print(f"finished at {time.strftime('%X')}")


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# hemen yukarıdaki örneğimizdeki fonksiyon asenkron olsa ve senkron bir programa göre hızlı olsa da
# esas olan asenkron programların görev olarak çağırılmasıdır bu şekilde daha hızlı bir programımız olur.
# bunu da asyncio içindeki create_task() metodu ile yaparız.
import asyncio
import time


async def say_after(gecikme, konu):
    await asyncio.sleep(gecikme)
    print(konu)


async def main():
    loop = asyncio.get_event_loop()
    task1 = loop.create_task(say_after(1, 'hello'))  # task açarken(görev oluştururken) await kullanmayız
    task2 = loop.create_task(say_after(2, 'world'))  # task açarken(görev oluştururken) await kullanmayız
    print(f"started at {time.strftime('%X')}")
    await task1  # oluşturduğumuz görev çağırılırken await ile çağırırız.
    await task2  # oluşturduğumuz görev çağırılırken await ile çağırırız.
    print(f"finished at {time.strftime('%X')}")


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# create_task() yerine ensure_future() metodu da kullanılabilir aynı anlamdadır.
import asyncio
import time


async def myTask():
    time.sleep(1)
    print("Processing Task")


async def main():
    for i in range(5):
        asyncio.ensure_future(myTask())
    pending = asyncio.Task.all_tasks()  # çalıştırılacak olan tüm görevlerin objesini döner.Henüz daha
    # çalışmamış ama çalışacak görevler.
    print(pending)

    running = asyncio.Task.current_task()  # o anda çalışan görevin örneğini döner, None dönerse çalışan
    # bir görev yok demektir.
    print(running)


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
'''
gather() metodu ile de pek çok coroutine'yi, asenkron fonksiyonunu bir arada görevlendirebiliriz.
eğer gather() içindeki bu coroutinelerden herhangi biri iptal olursa, gather() içindaki diğer fonksiyon_
lar bundan etkilenmez ama gather() iptal olursa tüm gonsiyonlar iptal olur.
'''
import time
import asyncio


async def factorial(name, number):
    f = 1
    for i in range(2, number + 1):
        print(f"Task {name}: Compute factorial({i})...")
        await asyncio.sleep(1)
        f *= i
        if number == 0:
            print("burada sıfıra bölme hatası var ama program sonlanmadı, görev tamamlanana kadar devam etti")
            f / 0
    print(f"Task {name}: factorial({number}) = {f}")


async def main():
    # gather bizim için bir program dizisi hazırlayıp çalıştırıyor.
    await asyncio.gather(
        factorial("A", 2),
        factorial("B", 3),
        factorial("C", 4),
        factorial("D", 0),
    )


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# task() metodunun cancel() fonsiyonu ile askıda olan(yapılacak olan)görevi iptal edebiliriz.
import asyncio
import time


async def myTask():
    time.sleep(1)
    print("Processing Task")
    for task in asyncio.Task.all_tasks():
        print(task)  # yapılacak olan görevi listeliyoruz
        task.cancel()  # yapılacak olan görevi iptal ettik
        print(task)  # iptal edilen görev listesini baıyoruz.


async def main():
    for i in range(5):
        asyncio.ensure_future(myTask())


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# ancak cancel() metodu bazı durumlarda görevi iptal etmeyi garanti edemiyor ve görev çalışa biliyor
# bu sebeple iptal edilecek bir görev varsa bunun kesin iptali için çalışan görev içerisinde try except
# bloğunda yakalamamız gerekebilir.
# aşağıdaki kod bloğunu okurken önce main(), sonra bir görev olan cancel_me() fonksiyonunu okumanızı tavsiye ederim.
import asyncio
import time


async def cancel_me():
    print('cancel_me(): before sleep')  # bir defa çalışacak işiniz varsa burada yaptırabilirsiniz.do while gibi.
    try:
        # Bir saat bekle
        await asyncio.sleep(3600)
    except asyncio.CancelledError:  # cancel_me() aslında iptal bir görev ama bir saniyelin bekleme yaptırınca
        # cancel_me() çalışmaya başladı, yani cancel()iptal işe yaramadı ancak python bunun iptal olduğunu hafızasında
        # tutuyor ve biz de bundan faydalanarak burada görevin iptal olup olmadığını try except ile denetleyerek
        # burada asyncio.CancelledError ile yakalıyoruz.
        print('cancel_me(): cancel sleep')
        raise
    finally:
        print('cancel_me(): after sleep')


async def main():
    # cancel_me() görevi (task'ı) oluşturduk.
    task = asyncio.ensure_future(cancel_me())
    # Programı bir saniye bekletince sanki iptal olmamış gibi yoluna devam ediyor.
    await asyncio.sleep(1)
    task.cancel()  # her zaman görev iptal olmuyor dediğim nokta burası!
    print(task.cancelled())  # burada false çıktısı ile görevin iptal olmadığını görebiliriz.
    try:
        await task  # except bloğunun çalışması gerekirken try içindeki task çalışıyor.
    except asyncio.CancelledError:
        print("main(): cancel_me is cancelled now")
        print(task.cancelled())  # burada true çıktısı ile görevin iptal olduğunu anlayabiliriz.
        print(
            task.result())  # task'ın o andaki sonucunu döndürür, mesela burada bir traceback hatasının en alt satırında
    # CancelledError döndürür.
    # //print(task.exception())#task ın CancelledError veya InvalidStateError hatasını döndürür.


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# task metodlarından result() aşağıda görev bittiğinin sonucunu 3 olarak döüyor.
import asyncio
import time


async def cancel_me():
    await asyncio.sleep(3)
    return 3  # bu satır olmasaydı task.result() sonucu None olurdu.


async def main():
    task = asyncio.ensure_future(cancel_me())
    await task
    print(task.result())  # task sonucunu alıyoruz.


# //print(task.exception())#task için bir hata olmadığından None döner.
# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# get_stack() metodu
import asyncio
import time


async def cancel_me():
    await asyncio.sleep(3)
    return 3


async def main():
    task = asyncio.ensure_future(cancel_me())
    print(task.get_stack())  # yapılacak olan görevler için bir liste içerisinde çerçeve döner.argüman olarak limit=1
    # gibi sayılar verilebilir  ama maximum limitten farklı sayıda task varsa traceback hatası döner.
    # iptal edilen veya başarıyla tamamlanmış görevler için boş liste döner.get_stack() yerine
    # print_stack() metoduda kullanılabilirdi aynı görevi görür ama çıktısı frame değil fonksiyonun adı olurdu.
    await task


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# asyncio.shield() kullanımı:herhangi bir nedenden dolayı program sonlanırsa,  bu metod fonksiyonun çalışmasını iptal etmez
# onu çalıştırır.

# asyncio. shield() metodu
import asyncio
from aiorun import run, shutdown_waits_for


# aiorun modülü kurulmalıdır!
async def corofn():
    await asyncio.sleep(5)
    print('Çalıştı!')


async def main():
    try:
        # await shutdown_waits_for(corofn())#bu satırı yorumdan kaldırıp, aşağıdaki satır yoruma alınırsa program çalıştıktan sonra Ctrl+C yapsanız bile corofn fonksiyonunun çalıştığını görebiliriz.
        await asyncio.wait_for(asyncio.shield(corofn()),
                               timeout=1.0)  # programın çalışması 1 saniyeden uzun sürerse program iptal olur ancak shield() içindeki fonksiyon bu iptalden sonra bile çalışır, çünkü shield() onu koruyor.
    except asyncio.CancelledError:
        print('Program iptal edildi!')


run(main())
# shield ile herhangi bir fonksiyonu korumaya alıyoruz, eğer program herhangi bir nedenden dolayı
# sonlanırsa bile, shield() içindeki corofn() adlı fonksiyon yine de çalışır.


# asyncio.wait_for() kulanımı
# eğer bir fonksiyona belirli bir zamana kadar çalış, eğer bu zaman içerisinde çalışmazsan, bir daha
# çalışmana gerek yok, şeklinde bir kullanımı var.
import asyncio
import time


async def eternity():
    # bir saat bekletiyoruz eternity() fonksiyonunu
    await asyncio.sleep(3600)
    print('yay!')


async def main():
    try:
        await asyncio.wait_for(eternity(),
                               timeout=1.0)  # bir saniye içerisinde çalışırsan çalış, eğer çalışmazsan, çalışmaya uğraşma son bul(sona er).
    except asyncio.TimeoutError:
        print('Bir saniye doldu çalışmadın ve TimeoutError raise oldu(ortaya çıktı)!')


asyncio.run(main())

# asyncio.wait() kullanımı
# parametre olarak task olarak yarattığımız fonksiyonlar verilmelidir, eğer task yaratmadan direk olarak
# fonksiyonu verirsek, fonksiyon çalışması tamamlandığında herhangi bir kontrol imkanımız olmaz.
# (done, pending) şeklinde tamamlanmış ve yapılacak olan görev şeklinde set tiplerini döner.
import asyncio
import time


async def foo():
    return 42


async def main():
    coro = foo()
    done, pending = await asyncio.wait({coro})  # fonksiyon direk parametre olarak verilmiş.
    if coro in done:
        # bu dallanmış blok asla çalışmaz
        print("coro çalıştı ve tamamlandı")


# asyncio.run(main())
loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# if bloğunu kullanabilmek için, task oluşturuyoruz
import asyncio  # asenkron için modülx`
import time


async def foo():
    return 42


async def main():
    task = asyncio.ensure_future(foo())
    done, pending = await asyncio.wait({task})
    if task in done:
        # Foo() task olarak yaratıldığından fonksiyonun tamamlandığını veya askıda olduğunu
        # kontrol edebiliyoruz, bu şekilde de görev tamamlanınca bu blok çalıştırılabiliyor.
        print("coro çalıştı ve tamamlandı")


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# wait() de timeout parametresi kullanıldığında yani verilen görev belirli bir zamana kadar çalışmasını
# bitirmezse bu timeout paremetresi sayesinde programı sonlandırabiliyoruz, ama burada wait_for gibi
# bir TimeoutError çıkışı(raise) yapmaz program bu yüzden bunun kontrolünü askıda kalan(çalışmayan)
# görev var mı diye sorgulamasını yaparız.
import asyncio  # asenkron için modül
import time


async def foo():
    await asyncio.sleep(7)
    return 42


async def main():
    task = asyncio.create_task(foo())
    done, pending = await asyncio.wait({task}, timeout=5.0)  # 5 saniyede programı tamamla yoksa görev yapılmaz diyoruz.
    if task in done:
        # Görev tamamlanırsa burası çalışır.
        print("yapıldı")
    if task in pending:
        print("5 saniye içinde yapılmadığından program sonlandı.(cancel)")


asyncio.run(main())
# wait()'e parametre olarak verebileceğimiz return_when adlı bir parametre daha var ancak kullanımı gereksiz
# ön tanımlı olarak ALL_COMPLETED yani tüm görevler tamamlandığında veya iptal(cancel) olduğunda return oluyor.
# ek olarak return_when=FIRST_COMPLETED var bu da tüm görevlerden daha ziyade bir tane bile görev tamamlansa veya
# iptal olsa return olur, son olarak return_when=FIRST_EXCEPTION bu da herhangi bir görev hata doğurursa(raise)
# döner eğer hata doğurmadan görev sonlanırsa  ALL_COMPLETED eşdeğer bir dönüş(return) sağlar.

'''
as_completed() adlı Task metodu kullanımı:bu metod parametre olarak aldığı asenkron fonksiyonları, ileride çalışacak
bir obje olarak(Future) ve iterator biçiminde(sıralı olarak, bir sonraki fonksiyonu çalıştıracak) return eder.
timeout paremetresi ön tanımlı olarak None'dır ama istersek bu paremetreye integer bir değer(örn:5)
vererek program verilen sürede bitmezse asyncio.TimeoutError hatası doğurur(raise).
'''
import time
import asyncio


async def myWorker(number):
    # await asyncio.sleep(1)
    return number * 2


async def main(coros):
    # for fs in asyncio.as_completed(coros, timeout=1): ##bu döngü kullanılırsa program bir saniye
    ##içinde bitmezse ki myWorker fonksiyonunu da her çalışmasında 1 saniye bekleyecek
    ##asyncio.TimeoutError hatası doğurur.
    for fs in asyncio.as_completed(
            coros):  # Her çalışacak fonksiyonu(Future) (myworker fonksiyonunun farklı parametreler şeklinde alıyor) ve
        # alıp onları tek tek çalıştırabileceğimiz bir obje(Future objesi) olarak dönüyor.
        print(await fs)


coros = [myWorker(i) for i in
         range(5)]  # Liste üreteci sayesinde myWorker'a 0'dan 4'e kadar paremetreleri gönderiyoruz.

loop = asyncio.get_event_loop()
loop.run_until_complete(main(coros))
# asyncio.run(main(coros))

# ----------------*Future Objesi*---------------------------------------------------------------------------------
'''
Düşük seviyeli api ile (loops), yüksek seviyeli api (async/await) arasında köprü işlevi görüyor.
Kullanımı şuna benziyor.Biz bir fonksiyon yazıyoruz ve bu fonksiyonun gelecekte oluşacak sonucunu, 
fonksiyonda oluşabilecek hatalar veya fonksiyon hatasız sonuclanacaksa, şu fonksiyonu çalıştır şeklinde;
fonksiyonu istediğimiz gibi manipüle edebiliyoruz.

asyncio.ensure_future(obj, *, loop=None ) metodu bizim için belirli görevleri yerine getirecek şekilde
awaitable fonksiyonu parametre olarak alıp, onu işleyebilir.Yukarıda bahsedilen create_task() metoduyla
aynı işlevi görüyor.Bu şekilde başlatılan bir görev fonksiyon işini tamamlayıncaya veya iptal edilinceye 
kadar ana program çalışmaya devam eder.
'''

import asyncio


async def set_after(fut, delay, value):
    # *delay* kadar programı uyutuyoruz.
    await asyncio.sleep(delay)
    # *fut* adlı Future nesnesinin sonuç değerini value olarak ayarlayabiliyoruz.
    fut.set_result(value)


# fut.result() ile sonuç değerini de alabiliyoruz ancak burada gerek yok set_result bizim için zaten sonuç değerini return ediyor

async def main():
    # mevcutta çalışan loop nesnesini alıyoruz.Future objeleri yaratmak için gerekli bir kalıptır.
    loop = asyncio.get_event_loop()
    # Yeni bir future objesi yaratıyoruz.
    fut = loop.create_future()
    # "set_after()" coroutine fonksiyonunu paralel bir görev olrak çalıştırmak için bu satırı kulanıyoruz.
    # loop.createtask() yerine "asyncio.create_task()" veya "asyncio.ensure_future()" da kullanabiliriz.
    loop.create_task(set_after(fut, 1, '... world'))
    print('hello ...')
    # *fut* objesinden değer gelene dek program bekler ve sonucu basar.
    print(await fut)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
# future ile program iptal edilmedi ise şu sonucu dön, şeklinde bir komut da oluşturabiliriz.

import asyncio


async def cancel_or_not(fut):
    # bu satrıda fut.cancel() yapılırsa CanceledError hatası oluşur.(raise)
    if not fut.cancelled():
        fut.set_result(42)


async def main():
    # mevcutta çalışan loop nesnesini alıyoruz.Future objeleri yaratmak için gerekli bir kalıptır.
    loop = asyncio.get_running_loop()
    # Yeni bir future objesi yaratıyoruz.
    fut = loop.create_future()
    loop.create_task(cancel_or_not(fut))
    # *fut* objesinden değer gelene dek program bekler ve sonucu basar.
    print(await fut)


asyncio.run(main())

# add_done_callback(callback, *, context=None ) metoduyla Future objesi oluştuğunda bir fonksiyon ile
# bunu belirtebiliriz.
import asyncio


async def cancel_or_not(fut):
    if not fut.cancelled():
        fut.set_result(42)


async def main():
    # mevcutta çalışan loop nesnesini alıyoruz.Future objeleri yaratmak için gerekli bir kalıptır.
    loop = asyncio.get_running_loop()
    # Yeni bir future objesi yaratıyoruz.
    fut = loop.create_future()
    loop.create_task(cancel_or_not(fut))
    # *fut* objesinden değer gelene dek program bekler ve sonucu basar.
    print(await fut)
    fut.add_done_callback(print("fonksiyon çalışması bitti"))  # cancel_or_not çalışması bitince çalışır


# bu komutu şöyle de yazabiliriz.fut.add_done_callback(functools.partial(print, "Bitti"))
# loop.call_soon(print("fonksiyon çalışması bitti"))##cancel_or_not çalışması bitince çalışır, yukardaki
# satırda yer alan fut.add_done_callback komut yerine kullanılabilir.
asyncio.run(main())
